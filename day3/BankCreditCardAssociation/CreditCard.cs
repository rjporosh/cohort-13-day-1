public class CreditCard
{
    
    private decimal _balance;

   
    public CreditCard(string cardNumber, decimal creditLimit,DateTime expirationDate) 
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(cardNumber);
        //todo make sure credit card 16 digit and digit only. 
        // invalidcreditcard number exception (customException)
        ArgumentOutOfRangeException.ThrowIfNegativeOrZero(creditLimit);
        //todo Invalid Expiration Date or CardExcpired Custom Exception
        if (expirationDate <= DateTime.Now)
            throw new ArgumentOutOfRangeException(nameof(expirationDate));

        CardNumber = cardNumber;
        CreditLimit = creditLimit;
        ExpirationDate = expirationDate;
        _balance = 0;
    }

    public string CardNumber { get; }
    public decimal CreditLimit { get; }
    public decimal Balance => _balance;
    public DateTime ExpirationDate { get; }


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


    public void BillPayment(decimal amount)
    {

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