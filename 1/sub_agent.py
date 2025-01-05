import re
from rich.console import Console
from rich.panel import Panel
from litellm import completion
from tavily import TavilyClient

# Initialize the Rich Console
console = Console()

def gpt_sub_agent(prompt, search_query=None, previous_gpt_tasks=None, use_search=False, continuation=False):
    if previous_gpt_tasks is None:
        previous_gpt_tasks = []

    continuation_prompt = "Continuing from the previous answer, please complete the response."
    system_message = "Previous gpt tasks:\n" + "\n".join(f"Task: {task['task']}\nResult: {task['result']}" for task in previous_gpt_tasks)
    if continuation:
        prompt = continuation_prompt

    qna_response = None
    if search_query and use_search:
        tavily = TavilyClient(api_key="YOUR_API_KEY")
        qna_response = tavily.qna_search(query=search_query)
        console.print(f"QnA response: {qna_response}", style="yellow")

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": prompt}
    ]

    if qna_response:
        messages.append({"role": "user", "content": f"\nSearch Results:\n{qna_response}"})

    gpt_response = completion.create(
        model=SUB_AGENT_MODEL,
        messages=messages,
        max_tokens=4096
    )

    response_text = gpt_response.choices[0].message.content
    usage = gpt_response.usage

    console.print(Panel(response_text, title="[bold blue]gpt Sub-agent Result[/bold blue]", title_align="left", border_style="blue", subtitle="Task completed, sending result to gpt 👇"))
    console.print(f"Input Tokens: {usage.prompt_tokens}, Output Tokens: {usage.completion_tokens}, Total Tokens: {usage.total_tokens}")

    if usage.completion_tokens >= 4000:  # Threshold set to 4000 as a precaution
        console.print("[bold yellow]Warning:[/bold yellow] Output may be truncated. Attempting to continue the response.")
        continuation_response_text = gpt_sub_agent(prompt, search_query, previous_gpt_tasks, use_search, continuation=True)
        response_text += continuation_response_text

    return response_text
