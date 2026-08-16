namespace PetOwnership.Models;

public class AdoptionCertificate
{
    private readonly string _certificateNumber;
    private readonly DateTime _adoptionDate;
    private readonly string _adopterName;

    public string CertificateNumber => _certificateNumber;
    public DateTime AdoptionDate => _adoptionDate;
    public string AdopterName => _adopterName;

    public AdoptionCertificate(
        string certificateNumber,
        DateTime adoptionDate,
        string adopterName)
    {
        if (string.IsNullOrWhiteSpace(certificateNumber))
            throw new ArgumentException(
                "Certificate number is required.");

        if (string.IsNullOrWhiteSpace(adopterName))
            throw new ArgumentException(
                "Adopter name is required.");

        _certificateNumber = certificateNumber;
        _adoptionDate = adoptionDate;
        _adopterName = adopterName;
    }

    public int MonthsWithAdopter()
    {
        var today = DateTime.Today;

        var months =
            (today.Year - _adoptionDate.Year) * 12 +
            today.Month - _adoptionDate.Month;

        if (today.Day < _adoptionDate.Day)
            months--;

        return Math.Max(months, 0);
    }
}