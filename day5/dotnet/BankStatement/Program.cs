using BankStatement.Application;
using BankStatement.Domain.Services;
using BankStatement.Infrastructure.Seed;
using BankStatement.Presentation;

var seeder = new BankDataSeeder();

var accounts = seeder.Seed();

var statementGenerator = new StatementGenerator();

var statementService =
    new BankStatementService(statementGenerator);

var menu =
    new ConsoleMenu(
        accounts,
        statementService);

menu.Run();