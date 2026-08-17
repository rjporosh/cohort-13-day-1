public class AccountHolder
{
    public Guid Id { get; }
    public string FullName { get; private set; }

    public AccountHolder(Guid id, string fullName)
    {
        if (string.IsNullOrWhiteSpace(fullName))
            throw new ArgumentException("Name is required.");

        Id = id;
        FullName = fullName;
    }
}