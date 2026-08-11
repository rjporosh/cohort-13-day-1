public class CreditCard
{
    private decimal _balance;

    public CreditCard(string cardNumber, decimal creditLimit,DateTime expirationDate,Customer customer)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(cardNumber);
        ArgumentOutOfRangeException.ThrowIfNegativeOrZero(creditLimit);
        if (expirationDate <= DateTime.Now)
            throw new ArgumentOutOfRangeException(nameof(expirationDate));
        if (customer == null)
            throw new ArgumentNullException(nameof(customer));

        CardNumber = cardNumber;
        CreditLimit = creditLimit;
        ExpirationDate = expirationDate;
        Customer = customer;
        _balance = 0;
    }

    public string CardNumber { get; }
    public decimal CreditLimit { get; }
    public decimal Balance => _balance;
    public DateTime ExpirationDate { get; }

    public Customer Customer { get; }

    public void Charge(decimal amount)
    {
        if (IsExpired())
            throw new InvalidOperationException("Cannot charge an expired card.");
        if (amount <= 0)
            throw new ArgumentOutOfRangeException(nameof(amount));

        if (_balance + amount > CreditLimit)
            throw new InvalidOperationException("Charge exceeds credit limit.");

        _balance += amount;
    }

    public void MakePayment(decimal amount)
    {
        if (IsExpired())
            throw new InvalidOperationException("Cannot make payment on an expired card.");
        if (amount <= 0)
            throw new ArgumentOutOfRangeException(nameof(amount));

        if (amount > _balance)
            throw new InvalidOperationException("Payment exceeds current balance.");

        _balance -= amount;
    }
    
    public bool IsExpired()
    {
        return DateTime.Now > ExpirationDate;
    }
}