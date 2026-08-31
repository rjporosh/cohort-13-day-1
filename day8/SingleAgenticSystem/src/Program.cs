using Microsoft.Extensions.AI;
using OpenAI;
public static class Program
{
    public static async Task Main()
    {
        var connectionString =
        Environment.GetEnvironmentVariable("SQL_CONNECTION")
        ?? "Server=localhost,1433;Database=BankDemo;User Id=sa;        Password=CallCenter@123;TrustServerCertificate=True;       Encrypt=False;";

        IChatClient client =
            new OpenAIClient(Environment.GetEnvironmentVariable("OPENAI_API_KEY"))
                .GetChatClient("gpt-4o-mini")
                .AsIChatClient();
        // Azure:  new AzureOpenAIClient(uri, cred).GetChatClient(deployment).AsIChatClient();
        // Local:  new OllamaChatClient(new Uri("http://localhost:11434"), "llama3.1");

        var agent = new DatabaseAgent(client, new SqlTools(connectionString));
        Console.WriteLine("Welcome to our internal Agentic banking system. Ask what you want to know about our banking data.");
        Console.WriteLine("The agent will explore the database and answer in plain language.");
        Console.Write("So, what is your query today? > ");
        var question = Console.ReadLine();

        if (string.IsNullOrWhiteSpace(question))
        {
            Console.WriteLine("Question cannot be empty.");
            return;
        }
        var answer = await agent.AskAsync(question);
        Console.WriteLine("\n=== Answer ===\n" + answer);
    }
}
