from rich.console import Console
from rich.panel import Panel
from litellm import completion
from tavily import TavilyClient
from config import SUB_AGENT_MODEL, TAVILY_API_KEY, ORCHESTRATOR_MODEL

console = Console()


def gpt_sub_agent(prompt, search_query=None, previous_gpt_tasks=None, use_search=False, continuation=False):
    if previous_gpt_tasks is None:
        previous_gpt_tasks = []

    continuation_prompt = "Continuing from the previous answer, please complete the response."
    system_message = (
        "You are an expert assistant. Your goal is to execute tasks accurately, provide detailed explanations of your reasoning, "
        "and ensure the correctness and quality of any code. Always explain your thought process and validate your output thoroughly.\n\n"
        "Previous tasks:\n" +
        "\n".join(f"Task: {task['task']}\nResult: {task['result']}" for task in previous_gpt_tasks)
    )
    if continuation:
        prompt = continuation_prompt

    qna_response = None
    if search_query and use_search:
        tavily = TavilyClient(TAVILY_API_KEY)
        qna_response = tavily.qna_search(query=search_query)
        console.print(f"QnA response: {qna_response}", style="yellow")

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": prompt}
    ]

    if qna_response:
        messages.append({"role": "user", "content": f"\nSearch Results:\n{qna_response}"})

    response = completion(model=SUB_AGENT_MODEL, messages=messages)

    response_text = response['choices'][0]['message']['content']  # type: ignore

    console.print(Panel(response_text, title=f"[bold blue]Sub-agent {SUB_AGENT_MODEL} Result[/bold blue]", title_align="left",
                  border_style="blue", subtitle=f"Task completed, sending result to Orchestrator 👇 {ORCHESTRATOR_MODEL}"))

    if len(response_text) >= 4000:  # Threshold set to 4000 as a precaution
        console.print("[bold yellow]Warning:[/bold yellow] Output may be truncated. Attempting to continue the response.")
        continuation_response_text = gpt_sub_agent(
            prompt, search_query, previous_gpt_tasks, use_search, continuation=True)
        response_text += continuation_response_text

    return response_text
