namespace CarLicensePlate.Domain;

public class LicensePlate
{
    public string PlateNumber { get; }

    public DateTime RegistrationDate { get; }

    public DateTime ExpirationDate { get; }

    public LicensePlate(
        string plateNumber,
        DateTime registrationDate,
        DateTime expirationDate)
    {
        if (string.IsNullOrWhiteSpace(plateNumber))
            throw new ArgumentException(
                "Plate number is required.",
                nameof(plateNumber));

        if (expirationDate <= registrationDate)
            throw new ArgumentException(
                "Expiration date must be after registration date.");

        PlateNumber = plateNumber;
        RegistrationDate = registrationDate;
        ExpirationDate = expirationDate;
    }

    public bool IsValid()
    {
        return DateTime.Today >= RegistrationDate.Date &&
               DateTime.Today <= ExpirationDate.Date;
    }
}