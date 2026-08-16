namespace HospitalMedication.Domain;

public class Prescription
{
    public Patient Patient { get; }

    public Medication Medication { get; }

    public DateTime PrescribedAt { get; }

    public Prescription(
        Patient patient,
        Medication medication)
    {
        Patient = patient
            ?? throw new ArgumentNullException(nameof(patient));

        Medication = medication
            ?? throw new ArgumentNullException(nameof(medication));

        PrescribedAt = DateTime.Now;
    }
}