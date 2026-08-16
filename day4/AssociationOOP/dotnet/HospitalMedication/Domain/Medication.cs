namespace HospitalMedication.Domain;

public class Medication
{
    public string Name { get; }

    public MedicationType Type { get; }

    public Medication(
        string name,
        MedicationType type)
    {
        if (string.IsNullOrWhiteSpace(name))
            throw new ArgumentException(
                "Medication name is required.");

        Name = name;
        Type = type;
    }
}