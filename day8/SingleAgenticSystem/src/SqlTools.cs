// =====================================================================================
//  SINGLE-AGENT SYSTEM — "Database Analyst" agent in C#
//
//  Use case:  User asks a question in natural language ("How many accounts opened
//             in the last 30 days?"). ONE agent, in a loop, explores the schema and
//             writes read-only SQL to answer it. No sub-agents, no orchestrator.
//
//  Why a loop is needed: the agent can't answer in one shot. It must discover tables,
//             inspect columns, then query — each step depends on the previous result.
//             That is the whole point of an agent (vs. a single prompt->response call).
//
// ====================================================================================

using System.ComponentModel;
using System.Text;
using Microsoft.Data.SqlClient;
// -------------------------------------------------------------------------------------
// 1) TOOLS  — Tool design is where most of the quality lives.
//    Each method is annotated so the model gets a clean schema + description.
// -------------------------------------------------------------------------------------
public sealed class SqlTools(string connectionString)
{
    [Description("Lists all base tables in the database (schema-qualified, e.g. dbo.Accounts).")]
    public async Task<string> ListTables()
    {
        const string sql = @"SELECT TABLE_SCHEMA + '.' + TABLE_NAME AS FullName
                             FROM INFORMATION_SCHEMA.TABLES
                             WHERE TABLE_TYPE = 'BASE TABLE'
                             ORDER BY 1;";
        return await ReadAsText(sql);
    }

    [Description("Returns the columns, data types and nullability for one table. " +
                 "Call this before writing a query so you use real column names.")]
    public async Task<string> DescribeTable(
        [Description("Table name, optionally schema-qualified, e.g. 'dbo.Accounts' or 'Accounts'.")]
        string table)
    {
        var (schema, name) = SplitName(table);
        const string sql = @"SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
                             FROM INFORMATION_SCHEMA.COLUMNS
                             WHERE TABLE_NAME = @t AND (@s IS NULL OR TABLE_SCHEMA = @s)
                             ORDER BY ORDINAL_POSITION;";
        return await ReadAsText(sql, ("@t", name), ("@s", (object?)schema ?? DBNull.Value));
    }

    [Description("Runs a single READ-ONLY SELECT query and returns up to 50 rows as text. " +
                 "Never write, update, delete or run DDL — those are rejected.")]
    public async Task<string> RunQuery(
        [Description("A single T-SQL SELECT statement.")] string sql)
    {
        if (!IsReadOnlySelect(sql))
            return "REJECTED: only a single read-only SELECT statement is allowed.";

        return await ReadAsText(sql, rowCap: 50);
    }

    // ---- helpers -------------------------------------------------------------------

    // Pragmatic app-level guard. The REAL guarantee should come from connecting with a
    // DB login that only has SELECT rights — defence in depth, never trust one layer.
    private static bool IsReadOnlySelect(string sql)
    {
        var s = sql.Trim().TrimEnd(';').Trim();
        if (s.Contains(';')) return false;                       // no batching
        var lead = s.Split([' ', '\n', '\r', '\t'], 2)[0].ToUpperInvariant();
        if (lead is not ("SELECT" or "WITH")) return false;
        string[] banned =
            ["INSERT","UPDATE","DELETE","MERGE","DROP","ALTER","CREATE","TRUNCATE",
             "EXEC","EXECUTE","GRANT","REVOKE","INTO","XP_","SP_"];
        var upper = s.ToUpperInvariant();
        return !banned.Any(b => upper.Contains(b));
    }

    private static (string? schema, string name) SplitName(string table)
    {
        var parts = table.Replace("[", "").Replace("]", "").Split('.', 2);
        return parts.Length == 2 ? (parts[0], parts[1]) : (null, parts[0]);
    }

    private async Task<string> ReadAsText(string sql, params (string, object)[] ps)
        => await ReadAsText(sql, rowCap: 200, ps);

    private async Task<string> ReadAsText(string sql, int rowCap, params (string, object)[] ps)
    {
        await using var conn = new SqlConnection(connectionString);
        await conn.OpenAsync();
        await using var cmd = new SqlCommand(sql, conn) { CommandTimeout = 15 };
        foreach (var (k, v) in ps) cmd.Parameters.AddWithValue(k, v);

        await using var r = await cmd.ExecuteReaderAsync();
        var sb = new StringBuilder();
        for (int i = 0; i < r.FieldCount; i++) sb.Append(r.GetName(i)).Append(i < r.FieldCount - 1 ? " | " : "\n");

        int rows = 0;
        while (await r.ReadAsync() && rows++ < rowCap)
        {
            for (int i = 0; i < r.FieldCount; i++)
                sb.Append(r.IsDBNull(i) ? "NULL" : r.GetValue(i)?.ToString())
                  .Append(i < r.FieldCount - 1 ? " | " : "\n");
        }
        if (rows == 0) sb.Append("(no rows)\n");
        else if (rows > rowCap) sb.Append($"... (truncated at {rowCap} rows)\n");
        return sb.ToString();
    }
}
