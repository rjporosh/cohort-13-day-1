namespace LibraryManagement.Domain;

public enum MemberType
{
    Regular,
    Premium
}

public class Member
{
    private readonly List<BookLoan> _loans = new();

    public int Id { get; }

    public string Name { get; }

    public MemberType Type { get; }

    public IReadOnlyCollection<BookLoan> Loans =>
        _loans.AsReadOnly();

    public int MaximumBooks =>
        Type == MemberType.Premium ? 5 : 3;

    public Member(
        int id,
        string name,
        MemberType type)
    {
        if (id <= 0)
            throw new ArgumentException("Invalid member ID.");

        if (string.IsNullOrWhiteSpace(name))
            throw new ArgumentException("Name is required.");

        Id = id;
        Name = name;
        Type = type;
    }

    public void Borrow(BookCopy copy)
    {
        if (_loans.Count(x => !x.IsReturned) >= MaximumBooks)
            throw new InvalidOperationException(
                $"Member cannot borrow more than " +
                $"{MaximumBooks} books.");

        copy.Borrow();

        _loans.Add(
            new BookLoan(copy));
    }
}