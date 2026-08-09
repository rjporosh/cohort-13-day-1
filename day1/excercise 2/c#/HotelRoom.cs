public class HotelRoom
{
    private bool _isAvailable = true;

    public HotelRoom(int roomNumber, decimal pricePerNight)
    {
        ArgumentOutOfRangeException.ThrowIfNegativeOrZero(roomNumber);
        ArgumentOutOfRangeException.ThrowIfNegativeOrZero(pricePerNight);

        RoomNumber = roomNumber;
        PricePerNight = pricePerNight;
    }

    public int RoomNumber { get; }
    public decimal PricePerNight { get; }
    public bool IsAvailable => _isAvailable;

    public void Book()
    {
        if (!_isAvailable)
            throw new InvalidOperationException("Room is already booked.");

        _isAvailable = false;
    }

    public void Checkout()
    {
        if (_isAvailable)
            throw new InvalidOperationException("Room is already available.");

        _isAvailable = true;
    }
}