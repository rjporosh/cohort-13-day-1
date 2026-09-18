public class PushNotificationService : INotificationService
{
    private readonly string _platform = "App";
    // Could be "Web" as well.

    // To do Need Device Token, Body , max characters etc
    public void Send(NotificationRequest request)
    {
        var order = request.Order;

        var message =
            $"Your order #{order.Id} has been placed. " +
            $"Total: {order.GrandTotalAmount}";

        Console.WriteLine(
            $"PUSH NOTIFICATION\n" +
            $"Platform: {_platform}\n" +
            $"Message: {message}\n");
    }
}