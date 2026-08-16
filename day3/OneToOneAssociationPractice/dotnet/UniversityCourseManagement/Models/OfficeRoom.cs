namespace UniversityCourseManagement.Models;

public class OfficeRoom
{
    public string RoomNumber { get; }
    public string BuildingName { get; }
    public int Capacity { get; }

    public OfficeRoom(
        string roomNumber,
        string buildingName,
        int capacity)
    {
        if (string.IsNullOrWhiteSpace(roomNumber))
            throw new ArgumentException(
                "Room number is required.");

        if (string.IsNullOrWhiteSpace(buildingName))
            throw new ArgumentException(
                "Building name is required.");

        if (capacity <= 0)
            throw new ArgumentException(
                "Capacity must be greater than zero.");

        RoomNumber = roomNumber;
        BuildingName = buildingName;
        Capacity = capacity;
    }
}