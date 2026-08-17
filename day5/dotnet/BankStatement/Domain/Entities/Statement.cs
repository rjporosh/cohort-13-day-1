public class Statement
{
    private readonly List<StatementLine> _lines = new();

    public DateTime StartDate { get; }
    public DateTime EndDate { get; }

    public decimal OpeningBalance { get; }
    public decimal ClosingBalance { get; }

    public decimal TotalDebit { get; }
    public decimal TotalCredit { get; }

    public IReadOnlyCollection<StatementLine> Lines =>
        _lines.AsReadOnly();

    public Statement(
        DateTime startDate,
        DateTime endDate,
        decimal openingBalance,
        decimal closingBalance,
        decimal totalDebit,
        decimal totalCredit,
        IEnumerable<StatementLine> lines)
    {
        StartDate = startDate;
        EndDate = endDate;
        OpeningBalance = openingBalance;
        ClosingBalance = closingBalance;
        TotalDebit = totalDebit;
        TotalCredit = totalCredit;

        _lines.AddRange(lines);
    }
}