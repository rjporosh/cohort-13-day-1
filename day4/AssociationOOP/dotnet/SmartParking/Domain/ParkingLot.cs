namespace SmartParking.Domain;

public class ParkingLot
{
    private readonly List<ParkingSlot> _slots = new();
    private readonly List<ParkingSession> _sessions = new();

    public IReadOnlyCollection<ParkingSlot> Slots =>
        _slots.AsReadOnly();

    public IReadOnlyCollection<ParkingSession> Sessions =>
        _sessions.AsReadOnly();

    public ParkingLot(int numberOfSlots)
    {
        if (numberOfSlots <= 0)
            throw new ArgumentException(
                "Number of slots must be positive.");

        for (var i = 1; i <= numberOfSlots; i++)
        {
            _slots.Add(new ParkingSlot(i));
        }
    }

    public ParkingSession Enter(Vehicle vehicle)
    {
        var slot = _slots.FirstOrDefault(
            x => x.IsAvailable);

        if (slot is null)
            throw new InvalidOperationException(
                "Parking lot is full.");

        slot.Assign(vehicle);

        var session = new ParkingSession(
            vehicle,
            slot);

        _sessions.Add(session);

        return session;
    }

    public decimal Exit(
        ParkingSession session,
        DateTime exitTime,
        decimal hourlyRate)
    {
        if (!_sessions.Contains(session))
            throw new InvalidOperationException(
                "Invalid parking session.");

        var charge = session.CalculateCharge(
            exitTime,
            hourlyRate);

        session.Slot.Release();

        return charge;
    }
}