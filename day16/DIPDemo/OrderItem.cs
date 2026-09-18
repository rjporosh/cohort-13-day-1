public class OrderItem
{
    public int Id { get; set; }
    public string Name { get; set; } = string.Empty;
    public Decimal Price { get; set; }
    public int Quantity { get; set; }
    public Decimal TotalPrice => Price * Quantity;
}