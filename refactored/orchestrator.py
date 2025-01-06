# # F:\_AI\MCPServer\maestro\refactored\orchestrator.py
import re
from rich.console import Console
from rich.panel import Panel
import json
from litellm import completion
from config import ORCHESTRATOR_MODEL, SUB_AGENT_MODEL

console = Console()


def gpt_orchestrator(
    objective, file_content=None, previous_results=None, use_search=False
):
    console.print(f"\n[bold]Calling Orchestrator {ORCHESTRATOR_MODEL} for your objective[/bold]")
    previous_results_text = "\n".join(previous_results) if previous_results else "None"
    if file_content:
        console.print(
            Panel(
                f"File content:\n{file_content}",
                title="[bold blue]File Content[/bold blue]",
                title_align="left",
                border_style="blue",
            )
        )

    messages = [
        {
            "role": "system",
            "content": "You are a detailed and meticulous assistant. Your primary goal is to break down complex objectives into manageable sub-tasks, provide thorough reasoning, and ensure code correctness. Always explain your thought process step-by-step and validate any code for errors, improvements, and adherence to best practices."
        },
        {
            "role": "user",
            "content": f"Based on the following objective{' and file content' if file_content else ''}, and the previous sub-task results (if any), please break down the objective into the next sub-task, and create a concise and detailed prompt for a subagent so it can execute that task. IMPORTANT!!! when dealing with code tasks make sure you check the code for errors and provide fixes and support as part of the next sub-task. If you find any bugs or have suggestions for better code, please include them in the next sub-task prompt. Please assess if the objective has been fully achieved. If the previous sub-task results comprehensively address all aspects of the objective, include the phrase 'The task is complete:' at the beginning of your response. If the objective is not yet fully achieved, break it down into the next sub-task and create a concise and detailed prompt for a subagent to execute that task.:\n\nObjective: {objective}"
            + ("\nFile content:\n" + file_content if file_content else "")
            + f"\n\nPrevious sub-task results:\n{previous_results_text}",
        },
    ]

    if use_search:
        messages.append(
            {
                "role": "user",
                "content": "Please also generate a JSON object containing a single 'search_query' key, which represents a question that, when asked online, would yield important information for solving the subtask. The question should be specific and targeted to elicit the most relevant and helpful resources. Format your JSON like this, with no additional text before or after:\n{\"search_query\": \"<question>\"}\n",
            }
        )

    gpt_response = completion(model=ORCHESTRATOR_MODEL, messages=messages)
    response_text = gpt_response["choices"][0]["message"]["content"]  # type: ignore

    console.print(
        Panel(
            response_text,
            title=f"[bold green]Orchestrator - {ORCHESTRATOR_MODEL}[/bold green]",
            title_align="left",
            border_style="green",
            subtitle=f"Sending task to Sub-Agent👇{SUB_AGENT_MODEL}",
        )
    )

    search_query = None
    if use_search:
        json_match = re.search(r"{.*}", response_text, re.DOTALL)
        if json_match:
            json_string = json_match.group()
            try:
                search_query = json.loads(json_string)["search_query"]
                console.print(
                    Panel(
                        f"Search Query: {search_query}",
                        title="[bold blue]Search Query[/bold blue]",
                        title_align="left",
                        border_style="blue",
                    )
                )
                response_text = response_text.replace(json_string, "").strip()
            except json.JSONDecodeError as e:
                console.print(
                    Panel(
                        f"Error parsing JSON: {e}",
                        title="[bold red]JSON Parsing Error[/bold red]",
                        title_align="left",
                        border_style="red",
                    )
                )

    return response_text, file_content, search_query
