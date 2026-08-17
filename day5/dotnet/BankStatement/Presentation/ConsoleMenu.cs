using System.Globalization;
using BankStatement.Application;
using BankStatement.Shared.Utilities;

namespace BankStatement.Presentation;

public class ConsoleMenu
{
    private readonly IReadOnlyCollection<BankAccount> _accounts;
    private readonly BankStatementService _statementService;

    public ConsoleMenu(
        IReadOnlyCollection<BankAccount> accounts,
        BankStatementService statementService)
    {
        _accounts = accounts;
        _statementService = statementService;
    }

    public void Run()
    {
        while (true)
        {
            DisplayHeader();
            DisplayMenu();

            Console.Write("Choose an option: ");

            var input = Console.ReadLine();

            Console.WriteLine();

            switch (input)
            {
                case "1":
                    ListAccounts();
                    break;

                case "2":
                    ViewStatement();
                    break;

                case "3":
                    Console.WriteLine("Thank you for using the Bank Statement System.");
                    return;

                default:
                    Console.WriteLine("Invalid option.");
                    break;
            }

            Console.WriteLine();
            Console.WriteLine("Press any key to continue...");
            Console.ReadKey();
            Console.Clear();
        }
    }

    private static void DisplayHeader()
    {
        Console.WriteLine("==============================================");
        Console.WriteLine("        BENGAL TRUST BANK LTD.");
        Console.WriteLine("           BANK STATEMENT SYSTEM");
        Console.WriteLine("==============================================");
        Console.WriteLine();
    }

    private static void DisplayMenu()
    {
        Console.WriteLine("1. List Accounts");
        Console.WriteLine("2. View Statement");
        Console.WriteLine("3. Exit");
        Console.WriteLine();
    }

    private void ListAccounts()
    {
        Console.WriteLine("Available Accounts");
        Console.WriteLine("------------------");

        foreach (var account in _accounts)
        {
            Console.WriteLine(
                $"{account.AccountNumber} | " +
                $"{account.AccountHolder.FullName} | " +
                $"{account.AccountType}");
        }
    }

    private void ViewStatement()
    {
        Console.Write("Enter account number: ");

        var accountNumber = Console.ReadLine();

        var account = _accounts.FirstOrDefault(
            x => x.AccountNumber == accountNumber);

        if (account is null)
        {
            Console.WriteLine("Account not found.");
            return;
        }

        var startDate = ReadDate("Enter start date (dd/MM/yyyy): ");
        var endDate = ReadDate("Enter end date (dd/MM/yyyy): ");

        try
        {
            var statement = _statementService.GetStatement(
                account,
                startDate,
                endDate);

            DisplayStatement(account, statement);
        }
        catch (ArgumentException ex)
        {
            Console.WriteLine($"Error: {ex.Message}");
        }
    }

    private static DateTime ReadDate(string message)
    {
        while (true)
        {
            Console.Write(message);

            var input = Console.ReadLine();

            if (DateTime.TryParseExact(
                    input,
                    "dd/MM/yyyy",
                    CultureInfo.InvariantCulture,
                    System.Globalization.DateTimeStyles.None,
                    out var date))
            {
                return date;
            }

            Console.WriteLine(
                "Invalid date. Please use dd/MM/yyyy.");
        }
    }

    private static void DisplayStatement(
        BankAccount account,
        Statement statement)
    {
        Console.Clear();

        Console.WriteLine("===============================================================");
        Console.WriteLine("                 BENGAL TRUST BANK LTD.");
        Console.WriteLine("                    ACCOUNT STATEMENT");
        Console.WriteLine("===============================================================");
        Console.WriteLine();

        Console.WriteLine(
            $"Account Holder : {account.AccountHolder.FullName}");

        Console.WriteLine(
            $"Account Number : {account.AccountNumber}");

        Console.WriteLine(
            $"Account Type   : {account.AccountType}");

        Console.WriteLine(
            $"Linked Card    : {account.LinkedCard.MaskedNumber}");

        Console.WriteLine(
            $"Currency       : {account.Currency}");

        Console.WriteLine(
            $"Period         : {DateFormatter.FormatRange(
                statement.StartDate,
                statement.EndDate)}");

        Console.WriteLine();

        Console.WriteLine(
            $"Opening Balance : {CurrencyFormatter.Format(
                statement.OpeningBalance)}");

        Console.WriteLine();

        Console.WriteLine(
            ConsoleTableFormatter.Format(statement.Lines));

        Console.WriteLine();

        Console.WriteLine("---------------------------------------------------------------");

        Console.WriteLine(
            $"Total Debits    : {CurrencyFormatter.Format(
                statement.TotalDebit)}");

        Console.WriteLine(
            $"Total Credits   : {CurrencyFormatter.Format(
                statement.TotalCredit)}");

        Console.WriteLine(
            $"Closing Balance : {CurrencyFormatter.Format(
                statement.ClosingBalance)}");

        Console.WriteLine("---------------------------------------------------------------");
    }
}