using EcommerceOrderManagement.Models;

Console.WriteLine("====================================");
Console.WriteLine("   E-COMMERCE ORDER MANAGEMENT");
Console.WriteLine("====================================");

var invoice = new Invoice(
    invoiceNumber: "INV-2026-001",
    invoiceDate: DateTime.Now,
    totalAmount: 10000m);

var order = new Order(
    orderId: 5001,
    customerName: "Porosh",
    orderDate: DateTime.Now,
    invoice: invoice,
    paymentStatus: PaymentStatus.Pending);

Console.WriteLine();
Console.WriteLine("ORDER");
Console.WriteLine($"Order ID      : {order.OrderId}");
Console.WriteLine($"Customer      : {order.CustomerName}");
Console.WriteLine($"Payment       : {order.PaymentStatus}");

Console.WriteLine();
Console.WriteLine("INVOICE");
Console.WriteLine($"Invoice       : {order.Invoice.InvoiceNumber}");
Console.WriteLine($"Amount        : {order.Invoice.TotalAmount:C}");
Console.WriteLine($"Tax 15%       : {order.Invoice.CalculateTax():C}");
Console.WriteLine(
    $"Grand Total   : {order.Invoice.CalculateGrandTotal():C}");

order.ChangePaymentStatus(PaymentStatus.Paid);

Console.WriteLine();
Console.WriteLine("ORDER SUMMARY");
Console.WriteLine("-------------");
Console.WriteLine(order.GenerateSummary());

Console.WriteLine();
Console.WriteLine("E-commerce application completed.");