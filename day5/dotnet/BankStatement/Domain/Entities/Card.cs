public class Card
{
    public string CardNumber { get; }
    public string MaskedNumber { get; }
    public string CardType { get; }

    public Card(
        string cardNumber,
        string cardType)
    {
        if (string.IsNullOrWhiteSpace(cardNumber))
            throw new ArgumentException("Card number is required.");

        CardNumber = cardNumber;
        CardType = cardType;

        MaskedNumber = MaskCardNumber(cardNumber);
    }

    private static string MaskCardNumber(string cardNumber)
    {
        if (cardNumber.Length < 4)
            throw new ArgumentException("Invalid card number.");

        return $"•••• •••• •••• {cardNumber[^4..]}";
    }
}