using CarLicensePlate.Domain;

var plate = new LicensePlate(
    "DHAKA-123456",
    DateTime.Today.AddYears(-1),
    DateTime.Today.AddYears(1));

var car = new Car(
    "John Doe",
    "Toyota",
    "Corolla",
    2020,
    plate);

Console.WriteLine("=== Car & License Plate ===");
Console.WriteLine();

Console.WriteLine($"Owner: {car.OwnerName}");
Console.WriteLine($"Manufacturer: {car.Manufacturer}");
Console.WriteLine($"Model: {car.Model}");
Console.WriteLine($"Manufacturing Year: {car.ManufacturingYear}");
Console.WriteLine($"Car Age: {car.GetAge()} years");

Console.WriteLine();

Console.WriteLine($"Plate: {car.LicensePlate.PlateNumber}");
Console.WriteLine($"Plate Valid: {car.LicensePlate.IsValid()}");
Console.WriteLine(
    $"Renewal Eligible: {car.IsEligibleForRenewal()}");