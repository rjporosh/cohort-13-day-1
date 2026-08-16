namespace SchoolManagement.Models;

public class Student
{
    private const double MinimumAttendance = 75.0;

    private double _attendancePercentage;

    public int StudentId { get; }
    public string Name { get; }
    public string GradeLevel { get; }

    public StudentIdCard IdCard { get; }

    public double AttendancePercentage =>
        _attendancePercentage;

    public Student(
        int studentId,
        string name,
        string gradeLevel,
        StudentIdCard idCard,
        double attendancePercentage)
    {
        if (studentId <= 0)
            throw new ArgumentException(
                "Student ID must be greater than zero.");

        if (string.IsNullOrWhiteSpace(name))
            throw new ArgumentException(
                "Student name is required.");

        if (string.IsNullOrWhiteSpace(gradeLevel))
            throw new ArgumentException(
                "Grade level is required.");

        if (attendancePercentage < 0 ||
            attendancePercentage > 100)
            throw new ArgumentException(
                "Attendance must be between 0 and 100.");

        IdCard = idCard ??
                 throw new ArgumentNullException(nameof(idCard));

        StudentId = studentId;
        Name = name;
        GradeLevel = gradeLevel;
        _attendancePercentage = attendancePercentage;
    }

    public bool IsAttendanceBelowMinimum()
    {
        return _attendancePercentage < MinimumAttendance;
    }

    public void UpdateAttendance(double percentage)
    {
        if (percentage < 0 || percentage > 100)
            throw new ArgumentException(
                "Attendance must be between 0 and 100.");

        _attendancePercentage = percentage;
    }
}