namespace VehicleRentalSystem.Models;

public class Truck : Vehicle
{
    private const decimal MaintenanceFeePerDay = 100m;

    public Truck(
        string brand,
        string model,
        int yearOfManufacture,
        decimal rentalPricePerDay)
        : base(
            brand,
            model,
            yearOfManufacture,
            rentalPricePerDay)
    {
    }

    public override decimal CalculateRentalCost(int rentalDays)
    {
        decimal rentalCost =
            RentalPricePerDay * rentalDays;

        decimal maintenanceCost =
            MaintenanceFeePerDay * rentalDays;

        return rentalCost + maintenanceCost;
    }
}