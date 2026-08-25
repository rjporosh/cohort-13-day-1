namespace VehicleRentalSystem.Models;

public class Car : Vehicle
{
    public Car(
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

        int currentYear = DateTime.Now.Year;
        int vehicleAge = currentYear - YearOfManufacture;

        if (vehicleAge > 5)
        {
            totalCost *= 0.90m;
        }

        return totalCost;
    }
}