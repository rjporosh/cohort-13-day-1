namespace BankCustomerCreditCard.Domain;

public class CreditCard
{
    private const decimal DefaultCreditLimit = 500_000m;

    private decimal _spentAmount;

    public string CardNumber { get; }

    public DateTime ExpirationDate { get; }

    public decimal CreditLimit { get; }

    public decimal SpentAmount => _spentAmount;

    public decimal AvailableCredit => CreditLimit - _spentAmount;

    public CreditCard(
        string cardNumber,
        DateTime expirationDate)
    {
        if (string.IsNullOrWhiteSpace(cardNumber))
            throw new ArgumentException(
                "Card number is required.",
                nameof(cardNumber));

        if (!cardNumber.All(char.IsDigit))
            throw new ArgumentException(
                "Card number must contain only digits.",
                nameof(cardNumber));

        CardNumber = cardNumber;
        ExpirationDate = expirationDate;
        CreditLimit = DefaultCreditLimit;
    }

    public bool IsValid()
    {
        return ExpirationDate.Date >= DateTime.Today;
    }
    
    public void MakePurchase(decimal amount)
    {
        if (!IsValid())
            throw new InvalidOperationException(
                "Cannot make a purchase with an expired credit card.");

        if (amount <= 0)
            throw new ArgumentException(
                "Purchase amount must be greater than zero.",
                nameof(amount));

        if (amount > AvailableCredit)
            throw new InvalidOperationException(
                "Purchase exceeds available credit.");

        _spentAmount += amount;
    }
    
    public decimal GetOutstandingBalance()
    {
        return _spentAmount;
    }
}