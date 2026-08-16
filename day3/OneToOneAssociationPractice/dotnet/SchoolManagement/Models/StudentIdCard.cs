namespace SchoolManagement.Models;

public class StudentIdCard
{
    private readonly string _cardNumber;
    private readonly DateTime _issueDate;
    private readonly int _academicYear;
    private DateTime _expirationDate;

    public string CardNumber => _cardNumber;
    public DateTime IssueDate => _issueDate;
    public int AcademicYear => _academicYear;
    public DateTime ExpirationDate => _expirationDate;

    public StudentIdCard(
        string cardNumber,
        DateTime issueDate,
        DateTime expirationDate,
        int academicYear)
    {
        if (string.IsNullOrWhiteSpace(cardNumber))
            throw new ArgumentException("Card number is required.");

        if (expirationDate <= issueDate)
            throw new ArgumentException(
                "Expiration date must be after issue date.");

        if (academicYear <= 0)
            throw new ArgumentException(
                "Academic year must be valid.");

        _cardNumber = cardNumber;
        _issueDate = issueDate;
        _expirationDate = expirationDate;
        _academicYear = academicYear;
    }

    public bool IsValidForAcademicYear(int currentAcademicYear)
    {
        return DateTime.Today >= _issueDate.Date &&
               DateTime.Today <= _expirationDate.Date &&
               _academicYear == currentAcademicYear;
    }

    public int DaysUntilExpiration()
    {
        return Math.Max(
            (_expirationDate.Date - DateTime.Today).Days,
            0);
    }

    public void Renew(
        DateTime newExpirationDate,
        int newAcademicYear)
    {
        if (newExpirationDate <= _expirationDate)
            throw new ArgumentException(
                "New expiration must be later.");

        if (newAcademicYear <= _academicYear)
            throw new ArgumentException(
                "New academic year must be later.");

        _expirationDate = newExpirationDate;
    }
}