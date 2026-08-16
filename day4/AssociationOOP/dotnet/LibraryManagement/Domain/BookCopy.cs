namespace LibraryManagement.Domain;

public class BookCopy
{
    public string CopyNumber { get; }

    public Book Book { get; }

    public bool IsBorrowed { get; private set; }

    public BookCopy(
        string copyNumber,
        Book book)
    {
        if (string.IsNullOrWhiteSpace(copyNumber))
            throw new ArgumentException(
                "Copy number is required.");

        Book = book
            ?? throw new ArgumentNullException(nameof(book));

        CopyNumber = copyNumber;
    }

    public void Borrow()
    {
        if (IsBorrowed)
            throw new InvalidOperationException(
                "Book copy is already borrowed.");

        IsBorrowed = true;
    }

    public void Return()
    {
        IsBorrowed = false;
    }
}