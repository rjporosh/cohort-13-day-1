namespace VehicleRentalSystem.Models;

public class Bike : Vehicle
{
    public Bike(
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
        decimal totalCost = RentalPricePerDay * rentalDays;

        if (rentalDays > 7)
        {
            totalCost *= 0.85m;
        }

        return totalCost;
    }
}