public class Product
{
    private double _stock;

    public Product(string productName, double initialStock = 0)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(productName);
        ArgumentOutOfRangeException.ThrowIfNegative(initialStock);

        ProductName = productName;
        _stock = initialStock;
    }

    public string ProductName { get; }
    public double Stock => _stock;

    public void AddStock(double quantity)
    {
        if (quantity <= 0)
            throw new ArgumentOutOfRangeException(nameof(quantity));

        _stock += quantity;
    }

    public void Sell(double quantity)
    {
        if (quantity <= 0)
            throw new ArgumentOutOfRangeException(nameof(quantity));

        if (quantity > _stock)
            throw new InvalidOperationException("Insufficient stock.");

        _stock -= quantity;
    }
}