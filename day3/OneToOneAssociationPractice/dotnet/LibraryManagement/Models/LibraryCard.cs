namespace LibraryManagement.Models;

public class LibraryCard
{
    private readonly string _cardNumber;
    private readonly DateTime _issueDate;
    private DateTime _expirationDate;

    public string CardNumber => _cardNumber;
    public DateTime IssueDate => _issueDate;
    public DateTime ExpirationDate => _expirationDate;

    public LibraryCard(
        string cardNumber,
        DateTime issueDate,
        DateTime expirationDate)
    {
        if (string.IsNullOrWhiteSpace(cardNumber))
        {
            throw new ArgumentException(
                "Card number cannot be empty.",
                nameof(cardNumber));
        }

        if (expirationDate <= issueDate)
        {
            throw new ArgumentException(
                "Expiration date must be after issue date.",
                nameof(expirationDate));
        }

        _cardNumber = cardNumber;
        _issueDate = issueDate;
        _expirationDate = expirationDate;
    }

    public bool IsValid()
    {
        var today = DateTime.Today;

        return today >= _issueDate.Date &&
               today <= _expirationDate.Date;
    }

    public bool IsExpired()
    {
        return DateTime.Today > _expirationDate.Date;
    }

    public int DaysUntilExpiration()
    {
        var remainingDays =
            (_expirationDate.Date - DateTime.Today).Days;

        return Math.Max(remainingDays, 0);
    }

    public void Renew(DateTime newExpirationDate)
    {
        if (newExpirationDate <= _expirationDate)
        {
            throw new ArgumentException(
                "New expiration date must be after the current expiration date.");
        }

        _expirationDate = newExpirationDate;
    }
}