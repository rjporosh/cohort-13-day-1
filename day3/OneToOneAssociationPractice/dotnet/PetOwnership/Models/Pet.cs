namespace PetOwnership.Models;

public class Pet
{
    private DateTime _lastVaccinationDate;

    public int PetId { get; }
    public string Name { get; }
    public string Species { get; }
    public string Breed { get; }
    public int Age { get; }

    public AdoptionCertificate Certificate { get; }

    public DateTime LastVaccinationDate =>
        _lastVaccinationDate;

    public Pet(
        int petId,
        string name,
        string species,
        string breed,
        int age,
        DateTime lastVaccinationDate,
        AdoptionCertificate certificate)
    {
        if (petId <= 0)
            throw new ArgumentException(
                "Pet ID must be valid.");

        if (string.IsNullOrWhiteSpace(name))
            throw new ArgumentException(
                "Pet name is required.");

        if (string.IsNullOrWhiteSpace(species))
            throw new ArgumentException(
                "Species is required.");

        if (string.IsNullOrWhiteSpace(breed))
            throw new ArgumentException(
                "Breed is required.");

        if (age < 0)
            throw new ArgumentException(
                "Age cannot be negative.");

        Certificate = certificate ??
                      throw new ArgumentNullException(
                          nameof(certificate));

        PetId = petId;
        Name = name;
        Species = species;
        Breed = breed;
        Age = age;
        _lastVaccinationDate = lastVaccinationDate;
    }

    public bool IsVaccinationOverdue(
        int vaccinationValidityMonths = 12)
    {
        return _lastVaccinationDate
            .AddMonths(vaccinationValidityMonths)
            < DateTime.Today;
    }

    public void UpdateVaccination(
        DateTime vaccinationDate)
    {
        if (vaccinationDate > DateTime.Today)
            throw new ArgumentException(
                "Vaccination date cannot be in the future.");

        _lastVaccinationDate = vaccinationDate;
    }
}