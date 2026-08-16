namespace LibraryManagement.Domain;

public class Book
{
    private readonly List<BookCopy> _copies = new();

    public int Id { get; }

    public string Title { get; }

    public IReadOnlyCollection<BookCopy> Copies =>
        _copies.AsReadOnly();

    public Book(int id, string title)
    {
        if (id <= 0)
            throw new ArgumentException("Invalid book ID.");

        if (string.IsNullOrWhiteSpace(title))
            throw new ArgumentException("Title is required.");

        Id = id;
        Title = title;
    }

    public BookCopy AddCopy(string copyNumber)
    {
        var copy = new BookCopy(
            copyNumber,
            this);

        _copies.Add(copy);

        return copy;
    }
}