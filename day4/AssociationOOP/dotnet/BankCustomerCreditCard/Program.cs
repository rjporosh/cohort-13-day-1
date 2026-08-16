using BankCustomerCreditCard.Domain;

var creditCard = new CreditCard(
    "1234567890123456",
    DateTime.Today.AddYears(3));

var customer = new Customer(
    1,
    "John Doe",
    "john@example.com",
    creditCard);

Console.WriteLine("=== Bank Customer & Credit Card ===");
Console.WriteLine();

Console.WriteLine($"Customer ID: {customer.Id}");
Console.WriteLine($"Customer: {customer.Name}");
Console.WriteLine($"Email: {customer.Email}");

Console.WriteLine();

Console.WriteLine($"Card Number: {customer.CreditCard.CardNumber}");
Console.WriteLine(
    $"Expiration: {customer.CreditCard.ExpirationDate:yyyy-MM-dd}");
Console.WriteLine(
    $"Valid: {customer.CreditCard.IsValid()}");

Console.WriteLine(
    $"Credit Limit: {customer.CreditCard.CreditLimit:N2}");

Console.WriteLine(
    $"Available Credit: {customer.CreditCard.AvailableCredit:N2}");

Console.WriteLine();

customer.CreditCard.MakePurchase(25_000m);

Console.WriteLine("After purchase of 25,000:");

Console.WriteLine(
    $"Spent: {customer.CreditCard.SpentAmount:N2}");

Console.WriteLine(
    $"Available Credit: {customer.CreditCard.AvailableCredit:N2}");

Console.WriteLine(
    $"Outstanding Balance: " +
    $"{customer.CreditCard.GetOutstandingBalance():N2}");