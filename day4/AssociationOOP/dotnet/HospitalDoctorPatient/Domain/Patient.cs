namespace HospitalDoctorPatient.Domain;

public class Patient
{
    private readonly List<string> _medicalHistory = new();
    private readonly List<string> _treatments = new();
    private readonly List<Appointment> _appointments = new();

    public int Id { get; }

    public string Name { get; }

    public Doctor PrimaryDoctor { get; }

    public IReadOnlyCollection<string> MedicalHistory =>
        _medicalHistory.AsReadOnly();

    public IReadOnlyCollection<string> Treatments =>
        _treatments.AsReadOnly();

    public IReadOnlyCollection<Appointment> Appointments =>
        _appointments.AsReadOnly();

    public bool IsDischarged { get; private set; }

    public Patient(
        int id,
        string name,
        Doctor primaryDoctor)
    {
        if (id <= 0)
            throw new ArgumentException("Invalid patient ID.");

        if (string.IsNullOrWhiteSpace(name))
            throw new ArgumentException("Patient name is required.");

        PrimaryDoctor = primaryDoctor
            ?? throw new ArgumentNullException(nameof(primaryDoctor));

        Id = id;
        Name = name;
    }

    public void AddAppointment(DateTime date)
    {
        if (IsDischarged)
            throw new InvalidOperationException(
                "Discharged patient cannot receive appointments.");

        _appointments.Add(new Appointment(date));
    }

    public void AddDiagnosis(string diagnosis)
    {
        if (string.IsNullOrWhiteSpace(diagnosis))
            throw new ArgumentException(
                "Diagnosis is required.");

        _medicalHistory.Add(diagnosis);
    }

    public void AddTreatment(string treatment)
    {
        if (string.IsNullOrWhiteSpace(treatment))
            throw new ArgumentException(
                "Treatment is required.");

        _treatments.Add(treatment);
    }

    public void Discharge()
    {
        IsDischarged = true;
    }
}