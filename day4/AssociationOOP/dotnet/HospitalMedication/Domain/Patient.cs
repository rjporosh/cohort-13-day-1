namespace HospitalMedication.Domain;

public class Patient
{
    private readonly List<Prescription> _prescriptions = new();

    public int Id { get; }

    public string Name { get; }

    public IReadOnlyCollection<Prescription> Prescriptions =>
        _prescriptions.AsReadOnly();

    public Patient(int id, string name)
    {
        if (id <= 0)
            throw new ArgumentException("Invalid patient ID.");

        if (string.IsNullOrWhiteSpace(name))
            throw new ArgumentException("Patient name is required.");

        Id = id;
        Name = name;
    }

    internal void AddPrescription(Prescription prescription)
    {
        _prescriptions.Add(prescription);
    }
}