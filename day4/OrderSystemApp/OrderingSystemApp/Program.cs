Order order = new Order
{
    OrderId = 1,
    CustomerName = "John Doe",
    Items = new List<OrderItem>
    {
        new OrderItem { ItemId = 1, ProductName = "Product A", Price = 10.0m, Quantity = 2, IsLuxuraryItem = false },
        new OrderItem { ItemId = 2, ProductName = "Product B", Price = 15.0m, Quantity = 1, IsLuxuraryItem = true }
    }


};
order.GetCalculatedTotalAmount();

Console.WriteLine($"Order ID: {order.OrderId}");
Console.WriteLine($"Customer Name: {order.CustomerName}");
Console.WriteLine("Items:");
foreach (var item in order.Items)
{
    Console.WriteLine($"- {item.ProductName} (Price: {item.Price}, Quantity: {item.Quantity})");
}
Console.WriteLine($"Total Amount: {order.TotalAmount}");    

