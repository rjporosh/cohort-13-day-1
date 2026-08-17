namespace BankStatement.Domain.Services;

public class StatementGenerator : IStatementGenerator
{
    public Statement Generate(
        BankAccount account,
        DateTime startDate,
        DateTime endDate)
    {
        ArgumentNullException.ThrowIfNull(account);

        if (startDate.Date > endDate.Date)
        {
            throw new ArgumentException(
                "Start date cannot be later than end date.");
        }

        var transactions = account.Transactions
            .OrderBy(t => t.Date)
            .ThenBy(t => t.Id)
            .ToList();

        var openingBalance = CalculateOpeningBalance(
            account.OpeningBalance,
            transactions,
            startDate);

        var periodTransactions = transactions
            .Where(t =>
                t.Date.Date >= startDate.Date &&
                t.Date.Date <= endDate.Date)
            .ToList();

        var runningBalance = openingBalance;

        var statementLines = new List<StatementLine>();

        foreach (var transaction in periodTransactions)
        {
            decimal? debit = null;
            decimal? credit = null;

            if (transaction.Type == TransactionType.Debit)
            {
                debit = transaction.Amount;
                runningBalance -= transaction.Amount;
            }
            else
            {
                credit = transaction.Amount;
                runningBalance += transaction.Amount;
            }

            statementLines.Add(
                new StatementLine(
                    transaction.Date,
                    transaction.Description,
                    debit,
                    credit,
                    runningBalance));
        }

        var totalDebit = periodTransactions
            .Where(t => t.Type == TransactionType.Debit)
            .Sum(t => t.Amount);

        var totalCredit = periodTransactions
            .Where(t => t.Type == TransactionType.Credit)
            .Sum(t => t.Amount);

        return new Statement(
            startDate,
            endDate,
            openingBalance,
            runningBalance,
            totalDebit,
            totalCredit,
            statementLines);
    }

    private static decimal CalculateOpeningBalance(
        decimal initialBalance,
        IEnumerable<Transaction> transactions,
        DateTime startDate)
    {
        var balance = initialBalance;

        foreach (var transaction in transactions)
        {
            if (transaction.Date.Date >= startDate.Date)
            {
                break;
            }

            if (transaction.Type == TransactionType.Credit)
            {
                balance += transaction.Amount;
            }
            else
            {
                balance -= transaction.Amount;
            }
        }

        return balance;
    }
}