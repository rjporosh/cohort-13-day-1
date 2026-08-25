using System;

namespace VehicleRentalSystem
{
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

        public void DisplayVehicleInfo()
        {
            Console.WriteLine($"Vehicle Type       : {GetType().Name}");
            Console.WriteLine($"Brand              : {Brand}");
            Console.WriteLine($"Model              : {Model}");
            Console.WriteLine($"Year               : {YearOfManufacture}");
            Console.WriteLine($"Rental Price/Day   : ${RentalPricePerDay}");
        }
    }


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
            decimal rentalCost = RentalPricePerDay * rentalDays;

            decimal maintenanceCost =
                MaintenanceFeePerDay * rentalDays;

            return rentalCost + maintenanceCost;
        }
    }


    internal class Program
    {
        static void Main(string[] args)
        {
            Vehicle car = new Car(
                "Toyota",
                "Corolla",
                2018,
                80m);

            Vehicle bike = new Bike(
                "Yamaha",
                "R15",
                2022,
                30m);

            Vehicle truck = new Truck(
                "Volvo",
                "FH16",
                2020,
                200m);


            int carRentalDays = 10;
            int bikeRentalDays = 10;
            int truckRentalDays = 5;


            Console.WriteLine("===== VEHICLE RENTAL SYSTEM =====");
            Console.WriteLine();


            DisplayRentalInfo(
                car,
                carRentalDays);

            DisplayRentalInfo(
                bike,
                bikeRentalDays);

            DisplayRentalInfo(
                truck,
                truckRentalDays);


            Console.ReadKey();
        }


        static void DisplayRentalInfo(
            Vehicle vehicle,
            int rentalDays)
        {
            vehicle.DisplayVehicleInfo();

            Console.WriteLine(
                $"Rental Days        : {rentalDays}");

            decimal finalCost =
                vehicle.CalculateRentalCost(rentalDays);

            Console.WriteLine(
                $"Final Rental Cost  : ${finalCost:F2}");

            Console.WriteLine(
                "--------------------------------");
        }
    }
}