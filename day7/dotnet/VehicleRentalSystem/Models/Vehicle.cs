namespace VehicleRentalSystem.Models;

public abstract class Vehicle
{
    public string Brand { get; set; }
    public string Model { get; set; }
    public int YearOfManufacture { get; set; }
    public decimal RentalPricePerDay { get; set; }

    protected Vehicle(
        string brand,
        string model,
        int yearOfManufacture,
        decimal rentalPricePerDay)
    {
        Brand = brand;
        Model = model;
        YearOfManufacture = yearOfManufacture;
        RentalPricePerDay = rentalPricePerDay;
    }

    public abstract decimal CalculateRentalCost(int rentalDays);
}