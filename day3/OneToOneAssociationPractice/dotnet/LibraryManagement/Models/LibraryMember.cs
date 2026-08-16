namespace LibraryManagement.Models;

public class LibraryMember
{
    private const int MaximumBorrowingLimit = 5;

    private readonly List<string> _borrowedBooks = [];

    public int MemberId { get; }
    public string Name { get; }

    public LibraryCard Card { get; }

    public int BorrowedBookCount =>
        _borrowedBooks.Count;

    public IReadOnlyCollection<string> BorrowedBooks =>
        _borrowedBooks.AsReadOnly();

    public LibraryMember(
        int memberId,
        string name,
        LibraryCard card)
    {
        if (memberId <= 0)
        {
            throw new ArgumentException(
                "Member ID must be greater than zero.",
                nameof(memberId));
        }

        if (string.IsNullOrWhiteSpace(name))
        {
            throw new ArgumentException(
                "Member name cannot be empty.",
                nameof(name));
        }

        Card = card ??
               throw new ArgumentNullException(nameof(card));

        MemberId = memberId;
        Name = name;
    }

    public bool CanBorrowBook()
    {
        return Card.IsValid() &&
               _borrowedBooks.Count < MaximumBorrowingLimit;
    }

    public void BorrowBook(string bookTitle)
    {
        if (string.IsNullOrWhiteSpace(bookTitle))
        {
            throw new ArgumentException(
                "Book title cannot be empty.",
                nameof(bookTitle));
        }

        if (!Card.IsValid())
        {
            throw new InvalidOperationException(
                "The library card is invalid or expired.");
        }

        if (_borrowedBooks.Count >= MaximumBorrowingLimit)
        {
            throw new InvalidOperationException(
                $"A member cannot borrow more than {MaximumBorrowingLimit} books.");
        }

        _borrowedBooks.Add(bookTitle);
    }

    public void ReturnBook(string bookTitle)
    {
        if (!_borrowedBooks.Remove(bookTitle))
        {
            throw new InvalidOperationException(
                "The specified book is not currently borrowed.");
        }
    }

    public int GetRemainingBorrowingCapacity()
    {
        return MaximumBorrowingLimit -
               _borrowedBooks.Count;
    }
}