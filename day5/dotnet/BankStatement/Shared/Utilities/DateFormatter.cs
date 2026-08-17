namespace BankStatement.Shared.Utilities;

public static class DateFormatter
{
    public static string Format(DateTime date)
    {
        return date.ToString("dd MMM yyyy");
    }

    public static string FormatRange(
        DateTime startDate,
        DateTime endDate)
    {
        return $"{startDate:dd MMM} – {endDate:dd MMM yyyy}";
    }
}