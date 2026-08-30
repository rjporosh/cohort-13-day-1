using Microsoft.Extensions.AI;
public sealed class DatabaseAgent(IChatClient client, SqlTools tools, int maxSteps = 8)
{
    private const string SystemPrompt =
        """
        You are a careful data analyst working against a Microsoft SQL Server database.
        You can only READ. To answer a question:
          1. If unsure what exists, call ListTables.
          2. Call DescribeTable before writing SQL, so you use real column names.
          3. Write ONE SELECT and call RunQuery.
          4. When you have the answer, reply in plain language. Show the number and,
             briefly, how you got it. Do not invent tables or columns.
        Keep tool calls minimal. Stop as soon as the question is answered.
        """;

    private readonly ChatOptions _options = new()
    {
        ToolMode = ChatToolMode.Auto,
        Tools =
        [
            AIFunctionFactory.Create(tools.ListTables),
            AIFunctionFactory.Create(tools.DescribeTable),
            AIFunctionFactory.Create(tools.RunQuery),
        ]
    };

    public async Task<string> AskAsync(string question, CancellationToken ct = default)
    {
        var messages = new List<ChatMessage>
        {
            new(ChatRole.System, SystemPrompt),
            new(ChatRole.User, question)
        };

        for (int step = 1; step <= maxSteps; step++)
        {
            ChatResponse response = await client.GetResponseAsync(messages, _options, ct);
            messages.AddRange(response.Messages);
            var calls = response.Messages
                .SelectMany(m => m.Contents)
                .OfType<FunctionCallContent>()
                .ToList();

            if (calls.Count == 0)  
            {
                Console.WriteLine($"[step {step}] final answer");
                return response.Text;
            }
            foreach (var call in calls)
            {
                Console.WriteLine($"[step {step}] -> {call.Name}({Args(call)})");
                var fn = _options.Tools!.OfType<AIFunction>().First(t => t.Name == call.Name);

                object? result;
                try
                {
                    result = await fn.InvokeAsync(
                        new AIFunctionArguments(call.Arguments ?? new Dictionary<string, object?>()), ct);
                }
                catch (Exception ex)
                {
                    result = $"ERROR: {ex.Message}";  
                }

                messages.Add(new ChatMessage(ChatRole.Tool,
                    [new FunctionResultContent(call.CallId, result)]));
            }
        }

        return "I couldn't reach a confident answer within the step budget. " +
               "Try narrowing the question.";
    }

    private static string Args(FunctionCallContent c)
        => c.Arguments is null ? "" : string.Join(", ", c.Arguments.Select(kv => $"{kv.Key}={kv.Value}"));
}
