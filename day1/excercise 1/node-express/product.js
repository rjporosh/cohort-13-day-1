class Product {
    #stock;

    constructor(productName, initialStock = 0) {
        if (!productName?.trim()) {
            throw new Error("Product name cannot be empty.");
        }

        if (initialStock < 0) {
            throw new Error("Initial stock cannot be negative.");
        }

        this.productName = productName;
        this.#stock = initialStock;
    }

    get stock() {
        return this.#stock;
    }

    addStock(quantity) {
        if (quantity <= 0) {
            throw new Error("Quantity must be greater than zero.");
        }

        this.#stock += quantity;
    }

    sell(quantity) {
        if (quantity <= 0) {
            throw new Error("Quantity must be greater than zero.");
        }

        if (quantity > this.#stock) {
            throw new Error("Insufficient stock.");
        }

        this.#stock -= quantity;
    }
}