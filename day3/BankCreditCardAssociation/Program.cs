//Console.WriteLine("Hello, World!");

using System.Runtime.InteropServices.Marshalling;

CreditCard creditCard1 =  new CreditCard("1234-5678-9012-3456", 5000.00m, DateTime.Now.AddYears(3));
Customer customer1 = new Customer("John Doe", "john.doe@example.com", creditCard1);
    customer1.CreditCard.Charge(600.00m);

    Console.WriteLine($"Customer Balance: {customer1.CreditCard.Balance}");

    customer1.CreditCard.BillPayment(200.00m);
      Console.WriteLine($"Customer Balance: {customer1.CreditCard.Balance}");
    customer1.CreditCard.Charge(100.00m);
      Console.WriteLine($"Customer Balance: {customer1.CreditCard.Balance}");