using UniversityCourseManagement.Models;

Console.WriteLine("==================================");
Console.WriteLine("   UNIVERSITY COURSE MANAGEMENT");
Console.WriteLine("==================================");

var officeRoom = new OfficeRoom(
    roomNumber: "B-402",
    buildingName: "Science Building",
    capacity: 4);

var professor = new Professor(
    professorId: 2001,
    name: "Dr. Rahman",
    department: "Computer Science",
    contactDetails: "rahman@university.edu",
    officeRoom: officeRoom,
    weeklyOfficeHours: 8);

Console.WriteLine();
Console.WriteLine("PROFESSOR");
Console.WriteLine($"ID            : {professor.ProfessorId}");
Console.WriteLine($"Name          : {professor.Name}");
Console.WriteLine($"Department    : {professor.Department}");
Console.WriteLine($"Contact       : {professor.ContactDetails}");

Console.WriteLine();
Console.WriteLine("OFFICE ROOM");
Console.WriteLine($"Building      : {professor.OfficeRoom.BuildingName}");
Console.WriteLine($"Room          : {professor.OfficeRoom.RoomNumber}");
Console.WriteLine($"Capacity      : {professor.OfficeRoom.Capacity}");

Console.WriteLine();
Console.WriteLine($"Weekly Hours  : {professor.WeeklyOfficeHours}");
Console.WriteLine(
    $"Policy Valid  : {professor.FollowsOfficeHourPolicy()}");

Console.WriteLine();
Console.WriteLine("University application completed.");