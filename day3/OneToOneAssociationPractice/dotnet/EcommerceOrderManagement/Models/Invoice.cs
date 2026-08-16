namespace EcommerceOrderManagement.Models;

public class Invoice
{
    private readonly string _invoiceNumber;
    private readonly DateTime _invoiceDate;
    private decimal _totalAmount;

    public string InvoiceNumber => _invoiceNumber;
    public DateTime InvoiceDate => _invoiceDate;
    public decimal TotalAmount => _totalAmount;

    public Invoice(
        string invoiceNumber,
        DateTime invoiceDate,
        decimal totalAmount)
    {
        if (string.IsNullOrWhiteSpace(invoiceNumber))
            throw new ArgumentException(
                "Invoice number is required.");

        if (totalAmount < 0)
            throw new ArgumentException(
                "Total amount cannot be negative.");

        _invoiceNumber = invoiceNumber;
        _invoiceDate = invoiceDate;
        _totalAmount = totalAmount;
    }

    public decimal CalculateTax(decimal taxRate = 0.15m)
    {
        if (taxRate < 0)
            throw new ArgumentException(
                "Tax rate cannot be negative.");

        return _totalAmount * taxRate;
    }

    public decimal CalculateGrandTotal(
        decimal taxRate = 0.15m)
    {
        return _totalAmount + CalculateTax(taxRate);
    }
}