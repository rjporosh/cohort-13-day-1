
using System;

public class ParkingFeeCalculator
{
    public decimal CalculateFee(int parkedMinutes)
    {
        // Validate parking duration
        if (parkedMinutes <= 0)
        {
            throw new ArgumentOutOfRangeException(
                nameof(parkedMinutes),
                "Parking duration must be greater than zero."
            );
        }

        // Every started hour counts as a full hour
        int startedHours = (int)Math.Ceiling(parkedMinutes / 60.0);

        // First hour costs 50, every additional hour costs 30
        decimal fee = 50 + ((startedHours - 1) * 30);

        // Maximum parking fee is 200
        return Math.Min(fee, 200);
    }
}
