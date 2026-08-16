using PetOwnership.Models;

Console.WriteLine("==============================");
Console.WriteLine("      PET OWNERSHIP SYSTEM");
Console.WriteLine("==============================");

var certificate = new AdoptionCertificate(
    certificateNumber: "CERT-2026-001",
    adoptionDate: DateTime.Today.AddMonths(-8),
    adopterName: "Porosh");

var pet = new Pet(
    petId: 3001,
    name: "Milo",
    species: "Cat",
    breed: "Domestic Shorthair",
    age: 3,
    lastVaccinationDate: DateTime.Today.AddMonths(-14),
    certificate: certificate);

Console.WriteLine();
Console.WriteLine("PET");
Console.WriteLine($"Pet ID          : {pet.PetId}");
Console.WriteLine($"Name            : {pet.Name}");
Console.WriteLine($"Species         : {pet.Species}");
Console.WriteLine($"Breed           : {pet.Breed}");
Console.WriteLine($"Age             : {pet.Age}");

Console.WriteLine();
Console.WriteLine("ADOPTION CERTIFICATE");
Console.WriteLine(
    $"Certificate     : {pet.Certificate.CertificateNumber}");
Console.WriteLine(
    $"Adopter         : {pet.Certificate.AdopterName}");
Console.WriteLine(
    $"Adoption Date   : {pet.Certificate.AdoptionDate:dd-MM-yyyy}");
Console.WriteLine(
    $"Months Together : {pet.Certificate.MonthsWithAdopter()}");

Console.WriteLine();
Console.WriteLine("VACCINATION");
Console.WriteLine(
    $"Last Vaccination: {pet.LastVaccinationDate:dd-MM-yyyy}");
Console.WriteLine(
    $"Overdue         : {pet.IsVaccinationOverdue()}");

Console.WriteLine();
Console.WriteLine("Pet application completed.");