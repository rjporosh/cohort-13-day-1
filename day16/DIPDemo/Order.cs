public class Order
{
    public int Id { get; set; }

    public DateTime CreatedAt { get; set; }

    public int CustomerId { get; set; }

    public Customer Customer { get; set; } = new();

    public decimal GrandTotalAmount { get; set; }

    public List<OrderItem> Items { get; set; } = new();
}