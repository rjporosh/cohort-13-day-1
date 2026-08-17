public class BankAccount
{
    private readonly List<Transaction> _transactions = new();

    public string AccountNumber { get; }
    public AccountType AccountType { get; }
    public Currency Currency { get; }

    public AccountHolder AccountHolder { get; }
    public Card LinkedCard { get; }

    public decimal OpeningBalance { get; }

    public IReadOnlyCollection<Transaction> Transactions =>
        _transactions.AsReadOnly();

    public BankAccount(
        string accountNumber,
        AccountType accountType,
        Currency currency,
        AccountHolder accountHolder,
        Card linkedCard,
        decimal openingBalance)
    {
        if (string.IsNullOrWhiteSpace(accountNumber))
            throw new ArgumentException("Account number is required.");

        if (openingBalance < 0)
            throw new ArgumentException("Opening balance cannot be negative.");

        AccountNumber = accountNumber;
        AccountType = accountType;
        Currency = currency;
        AccountHolder = accountHolder;
        LinkedCard = linkedCard;
        OpeningBalance = openingBalance;
    }

    public void AddTransaction(Transaction transaction)
    {
        ArgumentNullException.ThrowIfNull(transaction);

        _transactions.Add(transaction);
    }
}