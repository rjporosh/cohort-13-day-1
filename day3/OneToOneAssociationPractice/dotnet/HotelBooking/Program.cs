using HotelBooking.Models;

Console.WriteLine("==============================");
Console.WriteLine("       HOTEL BOOKING SYSTEM");
Console.WriteLine("==============================");

var receipt = new BookingReceipt(
    receiptId: "REC-2026-001",
    bookingDate: DateTime.Today,
    totalAmountPaid: 15000m);

var booking = new HotelBooking.Models.HotelBooking(
    bookingId: 1001,
    guestName: "Porosh",
    checkInDate: new DateTime(2026, 8, 20),
    checkOutDate: new DateTime(2026, 8, 23),
    dailyRoomRate: 5000m,
    isConfirmed: true,
    receipt: receipt);

Console.WriteLine();
Console.WriteLine($"Booking ID     : {booking.BookingId}");
Console.WriteLine($"Guest          : {booking.GuestName}");
Console.WriteLine($"Check-in       : {booking.CheckInDate:dd-MM-yyyy}");
Console.WriteLine($"Check-out      : {booking.CheckOutDate:dd-MM-yyyy}");
Console.WriteLine($"Stay Duration  : {booking.StayDuration} days");
Console.WriteLine($"Daily Rate     : {booking.DailyRoomRate:C}");
Console.WriteLine($"Expected Total : {booking.ExpectedAmount:C}");

Console.WriteLine();
Console.WriteLine("RECEIPT");
Console.WriteLine($"Receipt ID     : {booking.Receipt.ReceiptId}");
Console.WriteLine($"Paid           : {booking.Receipt.TotalAmountPaid:C}");
Console.WriteLine($"Payment Valid  : {booking.ValidatePayment()}");

Console.WriteLine();
Console.WriteLine("Hotel application completed.");