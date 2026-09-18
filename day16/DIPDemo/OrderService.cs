public class OrderService
{
    private readonly IEnumerable<INotificationService> _notificationServices;

    public OrderService(
        IEnumerable<INotificationService> notificationServices)
    {
        _notificationServices = notificationServices;
    }

    public void HandleOrder(Order order)
    {

   // To do: Save order to Database
   // Notify About this Order

        var request = new NotificationRequest
        {
           Order = order
        };

        foreach (var service in _notificationServices)
        {
            service.Send(request);
        }
    }
}