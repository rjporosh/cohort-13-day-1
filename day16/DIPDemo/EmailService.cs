public class EmailService : INotificationService
{
    private readonly string _fromEmail = "no-reply@myshop.com";

    // To do Need Email From, Sent To , Body ,subject etc
    public void Send(NotificationRequest request)
    {
        var order = request.Order;

        var subject = $"Your order has been placed. Order ID: {order.Id}";

        var body =
            $"Dear {order.Customer.Name},\n\n" +
            $"Your order has been placed successfully.\n" +
            $"Order ID: {order.Id}\n" +
            $"Order Date: {order.CreatedAt}\n\n" +
            "Items:\n" +
            string.Join(
                "\n",
                order.Items.Select(item =>
                    $"{item.Name} x {item.Quantity} = {item.TotalPrice}")) +
            $"\n\nGrand Total: {order.GrandTotalAmount}";

        Console.WriteLine(
            $"EMAIL\n" +
            $"From: {_fromEmail}\n" +
            $"To: {order.Customer.Email}\n" +
            $"Subject: {subject}\n" +
            $"Body:\n{body}\n");
    }
}