public class Order
{
    public int OrderId { get; set; }
    public string CustomerName { get; set; }
    public List<OrderItem> Items { get; set; }
    public decimal TotalAmount { get; set; }

    public Order()
    {
        Items = new List<OrderItem>();
    }
   
    public void AddItem(OrderItem item)
    {
        Items.Add(item);
    }

    public void GetCalculatedTotalAmount()
    {
        TotalAmount = Items.Sum(item => item.Price * item.Quantity);
    }
}