public class ThirdPartyDataProvidingService : INotificationService
{
    private readonly string _apiEndpoint =
        "https://api.thirdparty.com/notify";

    // TODO: API endpoint, request body, authentication, etc.

    public void Send(NotificationRequest request)
    {
        var order = request.Order;

        var orderedItems = string.Join(
            "\n",
            order.Items.Select(item =>
                $"  - {item.Name} | " +
                $"Price: {item.Price} | " +
                $"Quantity: {item.Quantity} | " +
                $"Total: {item.TotalPrice}")
        );

        var message =
            $"Order #{order.Id} has been placed.\n" +
            $"Customer Id: {order.Customer.Id}\n" +
            $"Customer Name: {order.Customer.Name}\n" +
            $"Customer Email: {order.Customer.Email}\n" +
            $"Customer Phone: {order.Customer.PhoneNumber}\n" +
            $"Ordered Items:\n{orderedItems}\n" +
            $"Grand Total: {order.GrandTotalAmount}";

        Console.WriteLine(
            $"THIRD PARTY SERVICE\n" +
            $"API Endpoint: {_apiEndpoint}\n" +
            $"Message:\n{message}\n");
    }
}