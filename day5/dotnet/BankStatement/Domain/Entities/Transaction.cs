public class Transaction
{
    public Guid Id { get; }
    public DateTime Date { get; }
    public string Description { get; }
    public decimal Amount { get; }
    public TransactionType Type { get; }

    public Transaction(
        DateTime date,
        string description,
        decimal amount,
        TransactionType type)
    {
        if (amount <= 0)
            throw new ArgumentException("Amount must be greater than zero.");

        if (string.IsNullOrWhiteSpace(description))
            throw new ArgumentException("Description is required.");

        Id = Guid.NewGuid();
        Date = date;
        Description = description;
        Amount = amount;
        Type = type;
    }
}