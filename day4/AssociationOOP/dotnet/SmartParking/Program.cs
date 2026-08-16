using SmartParking.Domain;

var parkingLot = new ParkingLot(2);

var vehicle = new Vehicle("DHAKA-1234");

var session = parkingLot.Enter(vehicle);

Console.WriteLine("=== Smart Parking ===");
Console.WriteLine();

Console.WriteLine(
    $"Vehicle: {vehicle.LicensePlate}");

Console.WriteLine(
    $"Assigned Slot: {session.Slot.Number}");

Console.WriteLine(
    $"Available Slots: " +
    $"{parkingLot.Slots.Count(x => x.IsAvailable)}");

var exitTime = session.EntryTime.AddHours(3);

var charge = parkingLot.Exit(
    session,
    exitTime,
    100m);

Console.WriteLine();
Console.WriteLine($"Parking Charge: {charge:N2}");

Console.WriteLine(
    $"Available Slots: " +
    $"{parkingLot.Slots.Count(x => x.IsAvailable)}");