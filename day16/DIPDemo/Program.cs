var customer = new Customer
{
    Id = 1,
    Name = "Porosh",
    Email = "porosh@example.com",
    PhoneNumber = "01712345678"
};

var order = new Order
{
    Id = 1001,
    CreatedAt = DateTime.Now,
    CustomerId = customer.Id,
    Customer = customer,
    Items =
    [
        new OrderItem
        {
            Id = 1,
            Name = "Mechanical Keyboard",
            Price = 5000m,
            Quantity = 1
        },
        new OrderItem
        {
            Id = 2,
            Name = "Mouse",
            Price = 1500m,
            Quantity = 2
        }
    ]
};

order.GrandTotalAmount =
    order.Items.Sum(item => item.TotalPrice);


// Composition Root
var notificationServices =
    new List<INotificationService>
    {
        new EmailService(),
        new SmsService(),
        new PushNotificationService(),
        new ThirdPartyDataProvidingService()
    };


// Dependency Injection
var orderService =
    new OrderService(notificationServices);


// Application call
orderService.HandleOrder(order);