namespace RestaurantOrderManagement.Domain;

public class Customer
{
    public int Id { get; }

    public string Name { get; }

    public Customer(int id, string name)
    {
        if (id <= 0)
            throw new ArgumentException("Invalid customer ID.");

        if (string.IsNullOrWhiteSpace(name))
            throw new ArgumentException("Name is required.");

        Id = id;
        Name = name;
    }

    public Order CreateOrder(int orderId)
    {
        return new Order(orderId);
    }
}