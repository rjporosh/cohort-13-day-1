class Product:
    def __init__(self, product_name: str, initial_stock: float = 0):
        if not product_name or not product_name.strip():
            raise ValueError("Product name cannot be empty.")

        if initial_stock < 0:
            raise ValueError("Initial stock cannot be negative.")

        self._product_name = product_name
        self._stock = initial_stock

    @property
    def product_name(self) -> str:
        return self._product_name

    @property
    def stock(self) -> float:
        return self._stock

    def add_stock(self, quantity: float) -> None:
        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero.")

        self._stock += quantity

    def sell(self, quantity: float) -> None:
        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero.")

        if quantity > self._stock:
            raise ValueError("Insufficient stock.")

        self._stock -= quantity