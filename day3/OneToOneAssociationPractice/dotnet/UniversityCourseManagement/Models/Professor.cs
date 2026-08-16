namespace UniversityCourseManagement.Models;

public class Professor
{
    private const int MinimumWeeklyOfficeHours = 6;

    private int _weeklyOfficeHours;

    public int ProfessorId { get; }
    public string Name { get; }
    public string Department { get; }
    public string ContactDetails { get; }

    public OfficeRoom OfficeRoom { get; }

    public int WeeklyOfficeHours =>
        _weeklyOfficeHours;

    public Professor(
        int professorId,
        string name,
        string department,
        string contactDetails,
        OfficeRoom officeRoom,
        int weeklyOfficeHours)
    {
        if (professorId <= 0)
            throw new ArgumentException(
                "Professor ID must be valid.");

        if (string.IsNullOrWhiteSpace(name))
            throw new ArgumentException(
                "Professor name is required.");

        if (string.IsNullOrWhiteSpace(department))
            throw new ArgumentException(
                "Department is required.");

        if (string.IsNullOrWhiteSpace(contactDetails))
            throw new ArgumentException(
                "Contact details are required.");

        OfficeRoom = officeRoom ??
                     throw new ArgumentNullException(
                         nameof(officeRoom));

        ProfessorId = professorId;
        Name = name;
        Department = department;
        ContactDetails = contactDetails;

        SetWeeklyOfficeHours(weeklyOfficeHours);
    }

    public void SetWeeklyOfficeHours(int hours)
    {
        if (hours < 0)
            throw new ArgumentException(
                "Office hours cannot be negative.");

        _weeklyOfficeHours = hours;
    }

    public bool FollowsOfficeHourPolicy()
    {
        return _weeklyOfficeHours >=
               MinimumWeeklyOfficeHours;
    }
}