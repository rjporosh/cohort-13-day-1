namespace HotelBooking.Models;

public class BookingReceipt
{
    private readonly string _receiptId;
    private readonly DateTime _bookingDate;
    private readonly decimal _totalAmountPaid;

    public string ReceiptId => _receiptId;
    public DateTime BookingDate => _bookingDate;
    public decimal TotalAmountPaid => _totalAmountPaid;

    public BookingReceipt(
        string receiptId,
        DateTime bookingDate,
        decimal totalAmountPaid)
    {
        if (string.IsNullOrWhiteSpace(receiptId))
            throw new ArgumentException(
                "Receipt ID is required.");

        if (totalAmountPaid < 0)
            throw new ArgumentException(
                "Payment cannot be negative.");

        _receiptId = receiptId;
        _bookingDate = bookingDate;
        _totalAmountPaid = totalAmountPaid;
    }

    public bool MatchesAmount(decimal expectedAmount)
    {
        return _totalAmountPaid == expectedAmount;
    }
}