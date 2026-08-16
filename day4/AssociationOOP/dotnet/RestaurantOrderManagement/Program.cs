using RestaurantOrderManagement.Domain;

var customer = new Customer(
    1,
    "John Doe");

var burger = new MenuItem(
    1,
    "Classic Burger",
    350m);

var coffee = new MenuItem(
    2,
    "Coffee",
    120m);

var order = customer.CreateOrder(1001);

order.AddItem(burger, 2);
order.AddItem(coffee, 2);

Console.WriteLine("=== Restaurant Order Management ===");
Console.WriteLine();

Console.WriteLine($"Customer: {customer.Name}");
Console.WriteLine($"Order: {order.Id}");
Console.WriteLine($"Status: {order.Status}");

Console.WriteLine(
    $"Total: {order.Total:N2}");

order.StartCooking();

Console.WriteLine(
    $"Status: {order.Status}");

order.Serve();

Console.WriteLine(
    $"Status: {order.Status}");

order.Pay();

Console.WriteLine(
    $"Paid: {order.IsPaid}");