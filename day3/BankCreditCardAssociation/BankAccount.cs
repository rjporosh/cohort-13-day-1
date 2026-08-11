public class BankAccount
{
    private decimal _balance;

    public BankAccount(string accountNumber, decimal initialBalance, Customer customer)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(accountNumber);
        ArgumentOutOfRangeException.ThrowIfNegative(initialBalance);
        if (customer == null)
            throw new ArgumentNullException(nameof(customer));

        AccountNumber = accountNumber;
        _balance = initialBalance;
        Customer = customer;
    }

    public string AccountNumber { get; }
    public decimal Balance => _balance;
    public Customer Customer { get; }

    public void Deposit(decimal amount)
    {
        if (amount <= 0)
            throw new ArgumentOutOfRangeException(nameof(amount));

        _balance += amount;
    }

    public void Withdraw(decimal amount)
    {
        if (amount <= 0)
            throw new ArgumentOutOfRangeException(nameof(amount));

        if (amount > _balance)
            throw new InvalidOperationException("Insufficient funds.");

        _balance -= amount;
    }
}