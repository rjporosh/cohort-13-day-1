using Microsoft.Extensions.AI;
public static class ProductionVariant
{
    public static async Task<string> Ask(IChatClient inner, SqlTools tools, string question)
    {
        IChatClient client = new ChatClientBuilder(inner)
            .UseFunctionInvocation(configure: f =>
            {
                f.MaximumIterationsPerRequest = 8;      
                f.AllowConcurrentInvocation   = false;  
                f.IncludeDetailedErrors       = true;
            })
            .Build();

        var options = new ChatOptions
        {
            ToolMode = ChatToolMode.Auto,
            Tools =
            [
                AIFunctionFactory.Create(tools.ListTables),
                AIFunctionFactory.Create(tools.DescribeTable),
                AIFunctionFactory.Create(tools.RunQuery),
            ]
        };

        var response = await client.GetResponseAsync(
        [
            new ChatMessage(ChatRole.System, "You are a careful read-only SQL analyst."),
            new ChatMessage(ChatRole.User, question)
        ], options);

        return response.Text;
    }
}
