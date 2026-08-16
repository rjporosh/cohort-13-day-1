using HospitalMedication.Domain;

var patient = new Patient(
    1,
    "John Doe");

var antibiotic = new Medication(
    "Amoxicillin",
    MedicationType.Antibiotic);

var statin = new Medication(
    "Atorvastatin",
    MedicationType.Statin);

var service = new PrescriptionService();

Console.WriteLine("=== Patient & Medication ===");
Console.WriteLine();

service.Prescribe(patient, antibiotic);

Console.WriteLine(
    $"Prescribed: {antibiotic.Name}");

try
{
    service.Prescribe(patient, statin);
}
catch (InvalidOperationException exception)
{
    Console.WriteLine(
        $"Prescription rejected: {exception.Message}");
}