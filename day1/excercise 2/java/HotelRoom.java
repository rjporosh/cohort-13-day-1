public class HotelRoom {
    private final int roomNumber;
    private final double pricePerNight;
    private boolean available = true;

    public HotelRoom(int roomNumber, double pricePerNight) {
        if (roomNumber <= 0) {
            throw new IllegalArgumentException("Room number must be greater than zero.");
        }

        if (pricePerNight <= 0) {
            throw new IllegalArgumentException("Price must be greater than zero.");
        }

        this.roomNumber = roomNumber;
        this.pricePerNight = pricePerNight;
    }

    public int getRoomNumber() {
        return roomNumber;
    }

    public double getPricePerNight() {
        return pricePerNight;
    }

    public booleanoli isAvailable() {
        return available;
    }

    public void book() {
        if (!available) {
            throw new IllegalStateException("Room is already booked.");
        }

        available = false;
    }

    public void checkout() {
        if (available) {
            throw new IllegalStateException("Room is already available.");
        }

        available = true;
    }
}