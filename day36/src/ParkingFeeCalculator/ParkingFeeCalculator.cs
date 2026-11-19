
using System;

namespace ParkingFeeCalculator;

public class ParkingFeeCalculator
{
    public decimal CalculateFee(int parkedMinutes)
    {
        if (parkedMinutes <= 0)
        {
            throw new ArgumentOutOfRangeException(
                nameof(parkedMinutes),
                "Parking duration must be greater than zero."
            );
        }

        int startedHours = (int)Math.Ceiling(parkedMinutes / 60.0);

        decimal fee = 50 + ((startedHours - 1) * 30);

        return Math.Min(fee, 200);
    }
}
