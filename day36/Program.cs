
using System;

class Program
{
    static void Main()
    {
        var calculator = new ParkingFeeCalculator();

        int[] testCases = { 1, 60, 61, 120, 121, 180, 241, 301, 600 };

        foreach (int minutes in testCases)
        {
            decimal fee = calculator.CalculateFee(minutes);

            Console.WriteLine(
                $"Parking: {minutes} minutes => Fee: {fee}"
            );
        }
    }
}