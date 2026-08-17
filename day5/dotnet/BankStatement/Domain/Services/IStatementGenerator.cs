public interface IStatementGenerator
{
    Statement Generate(
        BankAccount account,
        DateTime startDate,
        DateTime endDate);
}