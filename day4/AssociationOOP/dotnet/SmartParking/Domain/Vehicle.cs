namespace SmartParking.Domain;

public class Vehicle
{
    public string LicensePlate { get; }

    public Vehicle(string licensePlate)
    {
        if (string.IsNullOrWhiteSpace(licensePlate))
            throw new ArgumentException(
                "License plate is required.");

        LicensePlate = licensePlate;
    }
}