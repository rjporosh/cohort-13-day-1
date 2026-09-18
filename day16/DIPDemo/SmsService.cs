public class SmsService : INotificationService
{
    private readonly int _maxCharacters = 160;

    // To do Need Phone Number, Body , max characters etc
    public void Send(NotificationRequest request)
    {
        var order = request.Order;

        var message =
            $"Your order #{order.Id} has been placed. " +
            $"Total: {order.GrandTotalAmount}";

        if (message.Length > _maxCharacters)
        {
            message = message[.._maxCharacters];
        }

        Console.WriteLine(
            $"SMS\n" +
            $"To: {order.Customer.PhoneNumber}\n" +
            $"Message: {message}\n" +
            $"Length: {message.Length}/{_maxCharacters}\n");
    }
}