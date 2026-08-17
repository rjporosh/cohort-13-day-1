using System.Globalization;

namespace BankStatement.Shared.Utilities;

public static class CurrencyFormatter
{
    public static string Format(decimal amount)
    {
        return $"৳ {amount.ToString(
            "N2",
            CultureInfo.InvariantCulture)}";
    }
}