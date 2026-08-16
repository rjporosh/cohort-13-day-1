namespace HospitalMedication.Domain;

public class PrescriptionService
{
    public Prescription Prescribe(
        Patient patient,
        Medication medication)
    {
        ValidateCombination(patient, medication);

        var prescription = new Prescription(
            patient,
            medication);

        patient.AddPrescription(prescription);

        return prescription;
    }

    private static void ValidateCombination(
        Patient patient,
        Medication medication)
    {
        foreach (var prescription in patient.Prescriptions)
        {
            var existing = prescription.Medication.Type;
            var incoming = medication.Type;

            if (IsForbiddenCombination(existing, incoming))
            {
                throw new InvalidOperationException(
                    $"Cannot prescribe {medication.Name} " +
                    $"because it conflicts with " +
                    $"{prescription.Medication.Name}.");
            }
        }
    }

    private static bool IsForbiddenCombination(
        MedicationType first,
        MedicationType second)
    {
        return
            IsPair(
                first,
                second,
                MedicationType.Antibiotic,
                MedicationType.Statin)
            ||
            IsPair(
                first,
                second,
                MedicationType.MuscleRelaxant,
                MedicationType.CNSDepressant)
            ||
            IsPair(
                first,
                second,
                MedicationType.AntiInflammatory,
                MedicationType.Anticoagulant);
    }

    private static bool IsPair(
        MedicationType first,
        MedicationType second,
        MedicationType a,
        MedicationType b)
    {
        return (first == a && second == b) ||
               (first == b && second == a);
    }
}