classDiagram

    class Vehicle {
        <<abstract>>
        +string Brand
        +string Model
        +int YearOfManufacture
        +decimal RentalPricePerDay
        #Vehicle(string brand, string model, int yearOfManufacture, decimal rentalPricePerDay)
        +CalculateRentalCost(int rentalDays) decimal*
    }

    class Car {
        +Car(string brand, string model, int yearOfManufacture, decimal rentalPricePerDay)
        +CalculateRentalCost(int rentalDays) decimal
    }

    class Bike {
        +Bike(string brand, string model, int yearOfManufacture, decimal rentalPricePerDay)
        +CalculateRentalCost(int rentalDays) decimal
    }

    class Truck {
        -decimal MaintenanceFeePerDay
        +Truck(string brand, string model, int yearOfManufacture, decimal rentalPricePerDay)
        +CalculateRentalCost(int rentalDays) decimal
    }

    Vehicle <|-- Car
    Vehicle <|-- Bike
    Vehicle <|-- Truck