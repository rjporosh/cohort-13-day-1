namespace EcommerceOrderManagement.Models;

public class Order
{
    public int OrderId { get; }
    public string CustomerName { get; }

    public DateTime OrderDate { get; }

    public PaymentStatus PaymentStatus { get; private set; }

    public Invoice Invoice { get; }

    public Order(
        int orderId,
        string customerName,
        DateTime orderDate,
        Invoice invoice,
        PaymentStatus paymentStatus)
    {
        if (orderId <= 0)
            throw new ArgumentException(
                "Order ID must be valid.");

        if (string.IsNullOrWhiteSpace(customerName))
            throw new ArgumentException(
                "Customer name is required.");

        Invoice = invoice ??
                  throw new ArgumentNullException(nameof(invoice));

        OrderId = orderId;
        CustomerName = customerName;
        OrderDate = orderDate;
        PaymentStatus = paymentStatus;
    }

    public void ChangePaymentStatus(
        PaymentStatus newStatus)
    {
        PaymentStatus = newStatus;
    }

    public string GenerateSummary()
    {
        var tax = Invoice.CalculateTax();
        var total = Invoice.CalculateGrandTotal();

        return $"""
        Order ID: {OrderId}
        Customer: {CustomerName}
        Invoice: {Invoice.InvoiceNumber}
        Invoice Date: {Invoice.InvoiceDate:dd-MM-yyyy HH:mm}
        Amount: {Invoice.TotalAmount:C}
        Tax: {tax:C}
        Grand Total: {total:C}
        Payment Status: {PaymentStatus}
        """;
    }
}