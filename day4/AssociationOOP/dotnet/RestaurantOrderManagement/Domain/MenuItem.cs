namespace RestaurantOrderManagement.Domain;

public class MenuItem
{
    public int Id { get; }

    public string Name { get; }

    public decimal Price { get; }

    public MenuItem(
        int id,
        string name,
        decimal price)
    {
        if (id <= 0)
            throw new ArgumentException("Invalid menu item ID.");

        if (string.IsNullOrWhiteSpace(name))
            throw new ArgumentException("Name is required.");

        if (price <= 0)
            throw new ArgumentException(
                "Price must be positive.");

        Id = id;
        Name = name;
        Price = price;
    }
}