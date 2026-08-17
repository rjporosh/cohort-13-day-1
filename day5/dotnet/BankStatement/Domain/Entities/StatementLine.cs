public class StatementLine
{
    public DateTime Date { get; }
    public string Description { get; }

    public decimal? Debit { get; }
    public decimal? Credit { get; }

    public decimal Balance { get; }

    public StatementLine(
        DateTime date,
        string description,
        decimal? debit,
        decimal? credit,
        decimal balance)
    {
        Date = date;
        Description = description;
        Debit = debit;
        Credit = credit;
        Balance = balance;
    }
}