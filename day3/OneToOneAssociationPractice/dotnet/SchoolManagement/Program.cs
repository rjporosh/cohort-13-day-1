using SchoolManagement.Models;

Console.WriteLine("================================");
Console.WriteLine("     SCHOOL MANAGEMENT SYSTEM");
Console.WriteLine("================================");

var currentAcademicYear = 2026;

var idCard = new StudentIdCard(
    cardNumber: "STU-ID-2026-001",
    issueDate: new DateTime(2026, 1, 1),
    expirationDate: new DateTime(2026, 12, 31),
    academicYear: 2026);

var student = new Student(
    studentId: 1001,
    name: "Porosh",
    gradeLevel: "Grade 10",
    idCard: idCard,
    attendancePercentage: 82.5);

Console.WriteLine();
Console.WriteLine($"Student       : {student.Name}");
Console.WriteLine($"Student ID    : {student.StudentId}");
Console.WriteLine($"Grade         : {student.GradeLevel}");

Console.WriteLine();
Console.WriteLine("ID CARD");
Console.WriteLine($"Card Number   : {student.IdCard.CardNumber}");
Console.WriteLine($"Academic Year : {student.IdCard.AcademicYear}");
Console.WriteLine(
    $"Valid         : {student.IdCard.IsValidForAcademicYear(currentAcademicYear)}");
Console.WriteLine(
    $"Days Left     : {student.IdCard.DaysUntilExpiration()}");

Console.WriteLine();
Console.WriteLine("ATTENDANCE");
Console.WriteLine(
    $"Attendance    : {student.AttendancePercentage:F2}%");
Console.WriteLine(
    $"Below 75%     : {student.IsAttendanceBelowMinimum()}");

student.UpdateAttendance(72.5);

Console.WriteLine();
Console.WriteLine("After attendance update:");
Console.WriteLine(
    $"Attendance    : {student.AttendancePercentage:F2}%");
Console.WriteLine(
    $"Flagged       : {student.IsAttendanceBelowMinimum()}");

Console.WriteLine();
Console.WriteLine("School application completed.");