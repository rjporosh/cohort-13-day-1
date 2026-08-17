using System.Text;

namespace BankStatement.Shared.Utilities;

public static class ConsoleTableFormatter
{

    public static string Format(
        IEnumerable<StatementLine> lines)
    {
        ArgumentNullException.ThrowIfNull(lines);

        var statementLines = lines.ToList();

        var builder = new StringBuilder();

        const int dateWidth = 14;
        const int descriptionWidth = 42;
        const int debitWidth = 15;
        const int creditWidth = 15;
        const int balanceWidth = 17;

        builder.AppendLine(
            $"{PadRight("Date", dateWidth)}" +
            $"{PadRight("Description", descriptionWidth)}" +
            $"{PadLeft("Debit (৳)", debitWidth)}" +
            $"{PadLeft("Credit (৳)", creditWidth)}" +
            $"{PadLeft("Balance (৳)", balanceWidth)}");

        builder.AppendLine(new string('-', 103));

        foreach (var line in statementLines)
        {
            var date = DateFormatter.Format(line.Date);

            var description = Truncate(
                line.Description,
                descriptionWidth - 2);

            var debit = line.Debit.HasValue
                ? CurrencyFormatter.Format(line.Debit.Value)
                : "—";

            var credit = line.Credit.HasValue
                ? CurrencyFormatter.Format(line.Credit.Value)
                : "—";

            var balance = CurrencyFormatter.Format(line.Balance);

            builder.AppendLine(
                $"{PadRight(date, dateWidth)}" +
                $"{PadRight(description, descriptionWidth)}" +
                $"{PadLeft(debit, debitWidth)}" +
                $"{PadLeft(credit, creditWidth)}" +
                $"{PadLeft(balance, balanceWidth)}");
        }

        return builder.ToString();
    }

    private static string PadRight(
        string value,
        int width)
    {
        return value.PadRight(width);
    }

    private static string PadLeft(
        string value,
        int width)
    {
        return value.PadLeft(width);
    }

    private static string Truncate(
        string value,
        int maxLength)
    {
        if (value.Length <= maxLength)
            return value;

        return value[..(maxLength - 3)] + "...";
    }
}