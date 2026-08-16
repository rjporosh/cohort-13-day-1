using LibraryManagement.Models;

Console.WriteLine("==================================");
Console.WriteLine("     LIBRARY MANAGEMENT SYSTEM");
Console.WriteLine("==================================");

var card = new LibraryCard(
    cardNumber: "LIB-2026-0001",
    issueDate: DateTime.Today.AddMonths(-2),
    expirationDate: DateTime.Today.AddMonths(10));

var member = new LibraryMember(
    memberId: 1001,
    name: "Porosh",
    card: card);

Console.WriteLine();
Console.WriteLine("MEMBER INFORMATION");
Console.WriteLine("-------------------");

Console.WriteLine($"Member ID       : {member.MemberId}");
Console.WriteLine($"Name            : {member.Name}");

Console.WriteLine();
Console.WriteLine("LIBRARY CARD");
Console.WriteLine("------------");

Console.WriteLine($"Card Number     : {member.Card.CardNumber}");
Console.WriteLine($"Issue Date      : {member.Card.IssueDate:dd-MM-yyyy}");
Console.WriteLine($"Expiration Date : {member.Card.ExpirationDate:dd-MM-yyyy}");
Console.WriteLine($"Valid           : {member.Card.IsValid()}");
Console.WriteLine($"Expired         : {member.Card.IsExpired()}");
Console.WriteLine($"Days Remaining  : {member.Card.DaysUntilExpiration()}");

Console.WriteLine();
Console.WriteLine("BORROWING BOOKS");
Console.WriteLine("---------------");

member.BorrowBook("Clean Code");
member.BorrowBook("Design Patterns");
member.BorrowBook("Domain-Driven Design");

Console.WriteLine($"Borrowed Books : {member.BorrowedBookCount}");
Console.WriteLine(
    $"Remaining Limit: {member.GetRemainingBorrowingCapacity()}");

Console.WriteLine();
Console.WriteLine("BOOKS");
Console.WriteLine("-----");

foreach (var book in member.BorrowedBooks)
{
    Console.WriteLine($"- {book}");
}

Console.WriteLine();
Console.WriteLine("RETURNING BOOK");
Console.WriteLine("--------------");

member.ReturnBook("Clean Code");

Console.WriteLine($"Borrowed Books : {member.BorrowedBookCount}");
Console.WriteLine(
    $"Remaining Limit: {member.GetRemainingBorrowingCapacity()}");

Console.WriteLine();
Console.WriteLine("Application completed successfully.");