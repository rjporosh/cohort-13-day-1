namespace BankStatement.Infrastructure.Seed;

public class BankDataSeeder
{
    public IReadOnlyCollection<BankAccount> Seed()
    {
        var accounts = new List<BankAccount>
        {
            CreateRahimAccount(),
            CreateNusratAccount(),
            CreateTanvirAccount()
        };

        return accounts.AsReadOnly();
    }

    private static BankAccount CreateRahimAccount()
    {
        var holder = new AccountHolder(
            Guid.Parse("11111111-1111-1111-1111-111111111111"),
            "Rahim Uddin Ahmed");

        var card = new Card(
            "4212345678904471",
            "Visa Debit");

        var account = new BankAccount(
            "0142556788901023",
            AccountType.Savings,
            Currency.BDT,
            holder,
            card,
            85400m);

        account.AddTransaction(
            new Transaction(
                new DateTime(2026, 7, 3),
                "Salary Credit — Softworks Ltd.",
                65000m,
                TransactionType.Credit));

        account.AddTransaction(
            new Transaction(
                new DateTime(2026, 7, 5),
                "ATM Withdrawal — Dhanmondi 27",
                10000m,
                TransactionType.Debit));

        account.AddTransaction(
            new Transaction(
                new DateTime(2026, 7, 9),
                "POS Purchase — Agora Superstore",
                3250m,
                TransactionType.Debit));

        account.AddTransaction(
            new Transaction(
                new DateTime(2026, 7, 14),
                "Utility Bill — DESCO",
                2100m,
                TransactionType.Debit));

        account.AddTransaction(
            new Transaction(
                new DateTime(2026, 7, 18),
                "Fund Transfer — to A/C ••••7781",
                15000m,
                TransactionType.Debit));

        account.AddTransaction(
            new Transaction(
                new DateTime(2026, 7, 22),
                "Profit / Interest Credit",
                420m,
                TransactionType.Credit));

        account.AddTransaction(
            new Transaction(
                new DateTime(2026, 7, 27),
                "Online Purchase — Daraz",
                4780m,
                TransactionType.Debit));

        account.AddTransaction(
            new Transaction(
                new DateTime(2026, 7, 31),
                "Card Annual Fee",
                500m,
                TransactionType.Debit));

        return account;
    }

    private static BankAccount CreateNusratAccount()
    {
        var holder = new AccountHolder(
            Guid.Parse("22222222-2222-2222-2222-222222222222"),
            "Nusrat Jahan");

        var card = new Card(
            "4523456789017822",
            "Mastercard Debit");

        var account = new BankAccount(
            "0187654321098765",
            AccountType.Savings,
            Currency.BDT,
            holder,
            card,
            125000m);

        account.AddTransaction(
            new Transaction(
                new DateTime(2026, 7, 2),
                "Salary Credit — TechNova Ltd.",
                85000m,
                TransactionType.Credit));

        account.AddTransaction(
            new Transaction(
                new DateTime(2026, 7, 4),
                "Grocery Purchase — Unimart",
                6750m,
                TransactionType.Debit));

        account.AddTransaction(
            new Transaction(
                new DateTime(2026, 7, 8),
                "Mobile Recharge — Robi",
                500m,
                TransactionType.Debit));

        account.AddTransaction(
            new Transaction(
                new DateTime(2026, 7, 12),
                "Rent Payment",
                30000m,
                TransactionType.Debit));

        account.AddTransaction(
            new Transaction(
                new DateTime(2026, 7, 19),
                "Freelance Payment",
                25000m,
                TransactionType.Credit));

        account.AddTransaction(
            new Transaction(
                new DateTime(2026, 7, 23),
                "Restaurant Payment — Chillox",
                1250m,
                TransactionType.Debit));

        account.AddTransaction(
            new Transaction(
                new DateTime(2026, 7, 28),
                "Internet Bill — Link3",
                1200m,
                TransactionType.Debit));

        return account;
    }

    private static BankAccount CreateTanvirAccount()
    {
        var holder = new AccountHolder(
            Guid.Parse("33333333-3333-3333-3333-333333333333"),
            "Tanvir Hasan");

        var card = new Card(
            "4712345678909913",
            "Visa Debit");

        var account = new BankAccount(
            "0212345678903456",
            AccountType.Current,
            Currency.BDT,
            holder,
            card,
            210000m);

        account.AddTransaction(
            new Transaction(
                new DateTime(2026, 7, 1),
                "Business Revenue — Client Payment",
                120000m,
                TransactionType.Credit));

        account.AddTransaction(
            new Transaction(
                new DateTime(2026, 7, 6),
                "Office Rent",
                45000m,
                TransactionType.Debit));

        account.AddTransaction(
            new Transaction(
                new DateTime(2026, 7, 10),
                "Supplier Payment",
                28000m,
                TransactionType.Debit));

        account.AddTransaction(
            new Transaction(
                new DateTime(2026, 7, 15),
                "Client Payment — Project Alpha",
                75000m,
                TransactionType.Credit));

        account.AddTransaction(
            new Transaction(
                new DateTime(2026, 7, 20),
                "Electricity Bill — DPDC",
                8500m,
                TransactionType.Debit));

        account.AddTransaction(
            new Transaction(
                new DateTime(2026, 7, 25),
                "Office Supplies",
                4200m,
                TransactionType.Debit));

        account.AddTransaction(
            new Transaction(
                new DateTime(2026, 7, 30),
                "Bank Service Charge",
                750m,
                TransactionType.Debit));

        return account;
    }
}