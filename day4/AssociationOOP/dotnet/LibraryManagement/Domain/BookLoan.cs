namespace LibraryManagement.Domain;

public class BookLoan
{
    private const decimal RegularFinePerDay = 10m;

    public BookCopy Copy { get; }

    public DateTime BorrowedAt { get; }

    public DateTime DueDate { get; }

    public DateTime? ReturnedAt { get; private set; }

    public bool IsReturned => ReturnedAt.HasValue;

    public BookLoan(BookCopy copy)
    {
        Copy = copy
            ?? throw new ArgumentNullException(nameof(copy));

        BorrowedAt = DateTime.Today;
        DueDate = BorrowedAt.AddDays(14);
    }

    public decimal CalculateFine(
        DateTime returnDate,
        MemberType memberType)
    {
        if (returnDate <= DueDate)
            return 0;

        var lateDays =
            (returnDate.Date - DueDate.Date).Days;

        var rate =
            memberType == MemberType.Premium
                ? RegularFinePerDay / 2
                : RegularFinePerDay;

        return lateDays * rate;
    }

    public void Return(DateTime returnDate)
    {
        if (IsReturned)
            throw new InvalidOperationException(
                "Book has already been returned.");

        if (returnDate.Date < BorrowedAt.Date)
            throw new ArgumentException(
                "Return date cannot be before borrow date.");

        ReturnedAt = returnDate;

        Copy.Return();
    }
}