namespace RestaurantOrderManagement.Domain;

public enum OrderStatus
{
    Pending,
    Cooking,
    Served
}

public class Order
{
    private readonly List<OrderItem> _items = new();

    public int Id { get; }

    public OrderStatus Status { get; private set; }

    public bool IsPaid { get; private set; }

    public IReadOnlyCollection<OrderItem> Items =>
        _items.AsReadOnly();

    public decimal Total =>
        _items.Sum(x => x.Total);

    public Order(int id)
    {
        if (id <= 0)
            throw new ArgumentException(
                "Invalid order ID.");

        Id = id;
        Status = OrderStatus.Pending;
    }

    public void AddItem(
        MenuItem menuItem,
        int quantity)
    {
        if (Status != OrderStatus.Pending)
            throw new InvalidOperationException(
                "Items can only be added to pending orders.");

        _items.Add(
            new OrderItem(menuItem, quantity));
    }

    public void StartCooking()
    {
        EnsureHasItems();

        if (Status != OrderStatus.Pending)
            throw new InvalidOperationException(
                "Order is not pending.");

        Status = OrderStatus.Cooking;
    }

    public void Serve()
    {
        if (Status != OrderStatus.Cooking)
            throw new InvalidOperationException(
                "Order must be cooking before serving.");

        Status = OrderStatus.Served;
    }

    public void Pay()
    {
        if (Status != OrderStatus.Served)
            throw new InvalidOperationException(
                "Customer must receive the order before payment.");

        IsPaid = true;
    }

    private void EnsureHasItems()
    {
        if (_items.Count == 0)
            throw new InvalidOperationException(
                "Order must contain at least one item.");
    }
}