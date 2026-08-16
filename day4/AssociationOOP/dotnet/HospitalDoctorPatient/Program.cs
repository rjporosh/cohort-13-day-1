using HospitalDoctorPatient.Domain;

var doctor = new Doctor(
    1,
    "Dr. Sarah Ahmed");

var patient = doctor.AddPatient(
    101,
    "John Doe");

doctor.ScheduleAppointment(
    patient,
    DateTime.Now.AddDays(2));

doctor.Diagnose(
    patient,
    "Seasonal influenza");

doctor.PrescribeTreatment(
    patient,
    "Rest and prescribed medication");

Console.WriteLine("=== Hospital Doctor & Patient ===");
Console.WriteLine();

Console.WriteLine($"Doctor: {doctor.Name}");
Console.WriteLine($"Patient: {patient.Name}");

Console.WriteLine();
Console.WriteLine($"Appointments: {patient.Appointments.Count}");
Console.WriteLine($"Diagnoses: {patient.MedicalHistory.Count}");
Console.WriteLine($"Treatments: {patient.Treatments.Count}");
Console.WriteLine($"Discharged: {patient.IsDischarged}");