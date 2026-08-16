public class OrderItem
{
    public bool IsLuxuraryItem { get; set; }
    public int ItemId { get; set; }
    public required string ProductName { get; set; }
    public decimal Price { get; set
        {
            SetVat();
        } }
    public int Quantity { get; set; }

    public void SetVat()
    {
        if (IsLuxuraryItem)
        {
            Price += Price * 0.2m; // Add 20% VAT for luxury items
        }
        else
        {
            Price += Price * 0.1m; // Add 10% VAT for non-luxury items
        }
    }


    public decimal GetTotalPrice()
    {
        if(IsLuxuraryItem)
        {
            return Price * Quantity * 1.2m; // Add 20% VAT for luxury items
        }
        else
        {
            return Price * Quantity * 1.1m; // Add 10% VAT for non-luxury items
        }
    }
}