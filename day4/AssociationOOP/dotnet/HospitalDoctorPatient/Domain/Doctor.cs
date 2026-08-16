namespace HospitalDoctorPatient.Domain;

public class Doctor
{
    private readonly List<Patient> _patients = new();

    public int Id { get; }

    public string Name { get; }

    public IReadOnlyCollection<Patient> Patients =>
        _patients.AsReadOnly();

    public Doctor(int id, string name)
    {
        if (id <= 0)
            throw new ArgumentException("Invalid doctor ID.");

        if (string.IsNullOrWhiteSpace(name))
            throw new ArgumentException("Doctor name is required.");

        Id = id;
        Name = name;
    }

    public Patient AddPatient(int patientId, string patientName)
    {
        var patient = new Patient(
            patientId,
            patientName,
            this);

        _patients.Add(patient);

        return patient;
    }

    public void ScheduleAppointment(
        Patient patient,
        DateTime date)
    {
        EnsurePatientBelongsToDoctor(patient);

        patient.AddAppointment(date);
    }

    public void Diagnose(
        Patient patient,
        string diagnosis)
    {
        EnsurePatientBelongsToDoctor(patient);

        patient.AddDiagnosis(diagnosis);
    }

    public void PrescribeTreatment(
        Patient patient,
        string treatment)
    {
        EnsurePatientBelongsToDoctor(patient);

        patient.AddTreatment(treatment);
    }

    public void Discharge(Patient patient)
    {
        EnsurePatientBelongsToDoctor(patient);

        patient.Discharge();
    }

    private void EnsurePatientBelongsToDoctor(Patient patient)
    {
        if (!_patients.Contains(patient))
            throw new InvalidOperationException(
                "Patient does not belong to this doctor.");
    }
}