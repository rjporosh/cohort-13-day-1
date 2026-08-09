public class Product {
    private final String productName;
    private double stock;

    public Product(String productName) {
        this(productName, 0);
    }

    public Product(String productName, double initialStock) {
        if (productName == null || productName.isBlank()) {
            throw new IllegalArgumentException("Product name cannot be empty.");
        }

        if (initialStock < 0) {
            throw new IllegalArgumentException("Initial stock cannot be negative.");
        }

        this.productName = productName;
        this.stock = initialStock;
    }

    public String getProductName() {
        return productName;
    }

    public double getStock() {
        return stock;
    }

    public void addStock(double quantity) {
        if (quantity <= 0) {
            throw new IllegalArgumentException("Quantity must be greater than zero.");
        }

        stock += quantity;
    }

    public void sell(double quantity) {
        if (quantity <= 0) {
            throw new IllegalArgumentException("Quantity must be greater than zero.");
        }

        if (quantity > stock) {
            throw new IllegalStateException("Insufficient stock.");
        }

        stock -= quantity;
    }
}