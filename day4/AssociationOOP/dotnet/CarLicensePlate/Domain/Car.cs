namespace CarLicensePlate.Domain;

public class Car
{
    private const int MaximumRenewalAge = 20;

    public string OwnerName { get; }

    public string Manufacturer { get; }

    public string Model { get; }

    public int ManufacturingYear { get; }

    public LicensePlate LicensePlate { get; }

    public Car(
        string ownerName,
        string manufacturer,
        string model,
        int manufacturingYear,
        LicensePlate licensePlate)
    {
        if (string.IsNullOrWhiteSpace(ownerName))
            throw new ArgumentException(
                "Owner name is required.",
                nameof(ownerName));

        if (string.IsNullOrWhiteSpace(manufacturer))
            throw new ArgumentException(
                "Manufacturer is required.",
                nameof(manufacturer));

        if (string.IsNullOrWhiteSpace(model))
            throw new ArgumentException(
                "Model is required.",
                nameof(model));

        if (manufacturingYear <= 0 ||
            manufacturingYear > DateTime.Today.Year)
            throw new ArgumentException(
                "Invalid manufacturing year.",
                nameof(manufacturingYear));

        LicensePlate = licensePlate
            ?? throw new ArgumentNullException(nameof(licensePlate));

        OwnerName = ownerName;
        Manufacturer = manufacturer;
        Model = model;
        ManufacturingYear = manufacturingYear;
    }

    public int GetAge()
    {
        return DateTime.Today.Year - ManufacturingYear;
    }

    public bool IsEligibleForRenewal()
    {
        return GetAge() <= MaximumRenewalAge &&
               LicensePlate.IsValid();
    }
}