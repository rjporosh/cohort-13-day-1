namespace SmartParking.Domain;

public class ParkingSession
{
    public Vehicle Vehicle { get; }

    public ParkingSlot Slot { get; }

    public DateTime EntryTime { get; }

    public DateTime? ExitTime { get; private set; }

    public ParkingSession(
        Vehicle vehicle,
        ParkingSlot slot)
    {
        Vehicle = vehicle;
        Slot = slot;
        EntryTime = DateTime.Now;
    }

    public decimal CalculateCharge(
        DateTime exitTime,
        decimal hourlyRate)
    {
        if (exitTime < EntryTime)
            throw new ArgumentException(
                "Exit time cannot be before entry time.");

        if (hourlyRate <= 0)
            throw new ArgumentException(
                "Hourly rate must be positive.");

        ExitTime = exitTime;

        var duration = ExitTime.Value - EntryTime;

        var hours = Math.Ceiling(
            duration.TotalHours);

        return (decimal)hours * hourlyRate;
    }
}