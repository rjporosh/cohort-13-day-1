namespace SmartParking.Domain;

public class ParkingSlot
{
    public int Number { get; }

    public Vehicle? Vehicle { get; private set; }

    public bool IsAvailable => Vehicle is null;

    public ParkingSlot(int number)
    {
        if (number <= 0)
            throw new ArgumentException(
                "Slot number must be positive.");

        Number = number;
    }

    public void Assign(Vehicle vehicle)
    {
        if (!IsAvailable)
            throw new InvalidOperationException(
                "Parking slot is already occupied.");

        Vehicle = vehicle;
    }

    public void Release()
    {
        Vehicle = null;
    }
}