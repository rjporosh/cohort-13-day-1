using VehicleRentalSystem.Models;

namespace VehicleRentalSystem.Services;

public class RentalService
{
    public decimal CalculateRentalCost(
        Vehicle vehicle,
        int rentalDays)
    {
        return vehicle.CalculateRentalCost(rentalDays);
    }

    public void DisplayRentalSummary(
        Vehicle vehicle,
        int rentalDays)
    {
        decimal finalCost =
            CalculateRentalCost(vehicle, rentalDays);

        Console.WriteLine();
        Console.WriteLine("========================================");
        Console.WriteLine("           RENTAL SUMMARY");
        Console.WriteLine("========================================");

        Console.WriteLine(
            $"Vehicle Type   : {vehicle.GetType().Name}");

        Console.WriteLine(
            $"Brand          : {vehicle.Brand}");

        Console.WriteLine(
            $"Model          : {vehicle.Model}");

        Console.WriteLine(
            $"Year           : {vehicle.YearOfManufacture}");

        Console.WriteLine(
            $"Price Per Day  : ${vehicle.RentalPricePerDay:F2}");

        Console.WriteLine(
            $"Rental Days    : {rentalDays}");

        Console.WriteLine(
            $"Final Cost     : ${finalCost:F2}");

        Console.WriteLine("========================================");
    }
}