using BankStatement.Domain.Services;

namespace BankStatement.Application;

public class BankStatementService
{
    private readonly IStatementGenerator _statementGenerator;

    public BankStatementService(
        IStatementGenerator statementGenerator)
    {
        ArgumentNullException.ThrowIfNull(statementGenerator);

        _statementGenerator = statementGenerator;
    }

    public Statement GetStatement(
        BankAccount account,
        DateTime startDate,
        DateTime endDate)
    {
        return _statementGenerator.Generate(
            account,
            startDate,
            endDate);
    }
}