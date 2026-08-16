namespace HotelBooking.Models;

public class HotelBooking
{
    public int BookingId { get; }
    public string GuestName { get; }
    public DateTime CheckInDate { get; }
    public DateTime CheckOutDate { get; }
    public decimal DailyRoomRate { get; }

    public bool IsConfirmed { get; private set; }

    public BookingReceipt Receipt { get; }

    public int StayDuration =>
        (CheckOutDate.Date - CheckInDate.Date).Days;

    public decimal ExpectedAmount =>
        StayDuration * DailyRoomRate;

    public HotelBooking(
        int bookingId,
        string guestName,
        DateTime checkInDate,
        DateTime checkOutDate,
        decimal dailyRoomRate,
        bool isConfirmed,
        BookingReceipt receipt)
    {
        if (bookingId <= 0)
            throw new ArgumentException(
                "Booking ID must be valid.");

        if (string.IsNullOrWhiteSpace(guestName))
            throw new ArgumentException(
                "Guest name is required.");

        if (checkOutDate <= checkInDate)
            throw new ArgumentException(
                "Check-out must be after check-in.");

        if (dailyRoomRate <= 0)
            throw new ArgumentException(
                "Room rate must be greater than zero.");

        if (!isConfirmed)
            throw new InvalidOperationException(
                "A receipt can only be associated with a confirmed booking.");

        Receipt = receipt ??
                  throw new ArgumentNullException(nameof(receipt));

        BookingId = bookingId;
        GuestName = guestName;
        CheckInDate = checkInDate;
        CheckOutDate = checkOutDate;
        DailyRoomRate = dailyRoomRate;
        IsConfirmed = isConfirmed;
    }

    public bool ValidatePayment()
    {
        return Receipt.MatchesAmount(ExpectedAmount);
    }
}