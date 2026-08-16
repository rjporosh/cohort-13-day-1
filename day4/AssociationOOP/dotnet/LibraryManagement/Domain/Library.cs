namespace LibraryManagement.Domain;

public class Library
{
    private readonly List<Book> _books = new();
    private readonly List<Member> _members = new();

    public IReadOnlyCollection<Book> Books =>
        _books.AsReadOnly();

    public IReadOnlyCollection<Member> Members =>
        _members.AsReadOnly();

    public void AddBook(Book book)
    {
        if (!_books.Contains(book))
            _books.Add(book);
    }

    public void RegisterMember(Member member)
    {
        if (!_members.Contains(member))
            _members.Add(member);
    }
}