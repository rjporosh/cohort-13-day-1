namespace BankCustomerCreditCard.Domain;

public class Customer
{
    public int Id { get; }

    public string Name { get; }

    public string Email { get; }

    public CreditCard CreditCard { get; }

    public Customer(
        int id,
        string name,
        string email,
        CreditCard creditCard)
    {
        if (id <= 0)
            throw new ArgumentException(
                "Customer ID must be greater than zero.",
                nameof(id));

        if (string.IsNullOrWhiteSpace(name))
            throw new ArgumentException(
                "Customer name is required.",
                nameof(name));

        if (string.IsNullOrWhiteSpace(email))
            throw new ArgumentException(
                "Customer email is required.",
                nameof(email));

        CreditCard = creditCard
            ?? throw new ArgumentNullException(nameof(creditCard));

        Id = id;
        Name = name;
        Email = email;
    }
}