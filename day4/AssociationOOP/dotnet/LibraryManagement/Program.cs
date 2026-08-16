using LibraryManagement.Domain;

var library = new Library();

var book = new Book(
    1,
    "Clean Code");

var copy = book.AddCopy(
    "CC-001");

library.AddBook(book);

var regularMember = new Member(
    1,
    "John Doe",
    MemberType.Regular);

library.RegisterMember(
    regularMember);

regularMember.Borrow(copy);

Console.WriteLine("=== Library Management ===");
Console.WriteLine();

Console.WriteLine(
    $"Book: {book.Title}");

Console.WriteLine(
    $"Copy: {copy.CopyNumber}");

Console.WriteLine(
    $"Member: {regularMember.Name}");

Console.WriteLine(
    $"Member Type: {regularMember.Type}");

Console.WriteLine(
    $"Maximum Books: {regularMember.MaximumBooks}");

Console.WriteLine(
    $"Borrowed Books: {regularMember.Loans.Count}");

var loan = regularMember.Loans.First();

var returnDate = loan.DueDate.AddDays(3);

var fine = loan.CalculateFine(
    returnDate,
    regularMember.Type);

Console.WriteLine(
    $"Late Fine: {fine:N2}");

loan.Return(returnDate);

Console.WriteLine(
    $"Returned: {loan.IsReturned}");

Console.WriteLine(
    $"Copy Available: {!copy.IsBorrowed}");