using VehicleRentalSystem.Models;
using VehicleRentalSystem.Services;

namespace VehicleRentalSystem.UI;

public class ConsoleUI
{
    private readonly RentalService _rentalService;

    public ConsoleUI()
    {
        _rentalService = new RentalService();
    }

    public void Start()
    {
        while (true)
        {
            DisplayMainMenu();

            string? choice = Console.ReadLine();

            switch (choice)
            {
                case "1":
                    RentVehicle();
                    break;

                case "2":
                    Console.WriteLine(
                        "Thank you for using Vehicle Rental System.");

                    return;

                default:
                    Console.WriteLine(
                        "Invalid option. Please try again.");

                    Pause();
                    break;
            }
        }
    }

    private void DisplayMainMenu()
    {
        Console.Clear();

        Console.WriteLine("========================================");
        Console.WriteLine("       VEHICLE RENTAL SYSTEM");
        Console.WriteLine("========================================");
        Console.WriteLine();
        Console.WriteLine("1. Rent a Vehicle");
        Console.WriteLine("2. Exit");
        Console.WriteLine();
        Console.Write("Select an option: ");
    }

    private void RentVehicle()
    {
        Console.Clear();

        Console.WriteLine("========================================");
        Console.WriteLine("           SELECT VEHICLE");
        Console.WriteLine("========================================");
        Console.WriteLine();
        Console.WriteLine("1. Car");
        Console.WriteLine("2. Bike");
        Console.WriteLine("3. Truck");
        Console.WriteLine();

        Console.Write("Select vehicle type: ");

        string? choice = Console.ReadLine();

        Vehicle? vehicle = choice switch
        {
            "1" => CreateCar(),
            "2" => CreateBike(),
            "3" => CreateTruck(),
            _ => null
        };

        if (vehicle == null)
        {
            Console.WriteLine("Invalid vehicle type.");
            Pause();
            return;
        }

        int rentalDays = ReadPositiveInteger(
            "Enter rental days: ");

        _rentalService.DisplayRentalSummary(
            vehicle,
            rentalDays);

        Pause();
    }

    private Car CreateCar()
    {
        Console.WriteLine();
        Console.WriteLine("----- CAR INFORMATION -----");

        string brand = ReadText("Enter brand: ");
        string model = ReadText("Enter model: ");

        int year = ReadPositiveInteger(
            "Enter year of manufacture: ");

        decimal price = ReadPositiveDecimal(
            "Enter rental price per day: ");

        return new Car(
            brand,
            model,
            year,
            price);
    }

    private Bike CreateBike()
    {
        Console.WriteLine();
        Console.WriteLine("----- BIKE INFORMATION -----");

        string brand = ReadText("Enter brand: ");
        string model = ReadText("Enter model: ");

        int year = ReadPositiveInteger(
            "Enter year of manufacture: ");

        decimal price = ReadPositiveDecimal(
            "Enter rental price per day: ");

        return new Bike(
            brand,
            model,
            year,
            price);
    }

    private Truck CreateTruck()
    {
        Console.WriteLine();
        Console.WriteLine("----- TRUCK INFORMATION -----");

        string brand = ReadText("Enter brand: ");
        string model = ReadText("Enter model: ");

        int year = ReadPositiveInteger(
            "Enter year of manufacture: ");

        decimal price = ReadPositiveDecimal(
            "Enter rental price per day: ");

        return new Truck(
            brand,
            model,
            year,
            price);
    }

    private string ReadText(string message)
    {
        while (true)
        {
            Console.Write(message);

            string? input = Console.ReadLine();

            if (!string.IsNullOrWhiteSpace(input))
            {
                return input.Trim();
            }

            Console.WriteLine(
                "Value cannot be empty. Try again.");
        }
    }

    private int ReadPositiveInteger(string message)
    {
        while (true)
        {
            Console.Write(message);

            if (int.TryParse(
                    Console.ReadLine(),
                    out int value)
                && value > 0)
            {
                return value;
            }

            Console.WriteLine(
                "Please enter a valid positive number.");
        }
    }

    private decimal ReadPositiveDecimal(string message)
    {
        while (true)
        {
            Console.Write(message);

            if (decimal.TryParse(
                    Console.ReadLine(),
                    out decimal value)
                && value > 0)
            {
                return value;
            }

            Console.WriteLine(
                "Please enter a valid positive price.");
        }
    }

    private void Pause()
    {
        Console.WriteLine();
        Console.WriteLine(
            "Press any key to continue...");

        Console.ReadKey();
    }
}