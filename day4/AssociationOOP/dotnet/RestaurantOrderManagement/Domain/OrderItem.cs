namespace RestaurantOrderManagement.Domain;

public class OrderItem
{
    public MenuItem MenuItem { get; }

    public int Quantity { get; }

    public decimal Total =>
        MenuItem.Price * Quantity;

    public OrderItem(
        MenuItem menuItem,
        int quantity)
    {
        MenuItem = menuItem
            ?? throw new ArgumentNullException(nameof(menuItem));

        if (quantity <= 0)
            throw new ArgumentException(
                "Quantity must be positive.");

        Quantity = quantity;
    }
}