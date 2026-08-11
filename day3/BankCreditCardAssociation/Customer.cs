public class Customer
{
    public Customer(string name, string email,CreditCard creditCard)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(name);
        ArgumentException.ThrowIfNullOrWhiteSpace(email);
        if (creditCard == null)
            throw new ArgumentNullException(nameof(creditCard));

        Name = name;
        Email = email;
        CreditCard = creditCard;
    }
    public CreditCard CreditCard { get; }
    public string Name { get; }
    public string Email { get; }
}