# # # F:\_AI\MCPServer\maestro\refactored\maestro-anyapi.py
import re
from rich.console import Console
from rich.panel import Panel
from datetime import datetime
import json
from orchestrator import gpt_orchestrator
from sub_agent import gpt_sub_agent
from refiner import refine as anthropic_refine
from file_utils import create_folder_structure, read_file

console = Console()


def get_user_inputs():
    """Get inputs from the user."""
    objective = input("Please enter your objective: ")
    provide_file = input("Do you want to provide a file path? (y/n): ").lower() == "y"

    file_content = None
    if provide_file:
        file_path = input("Please enter the file path: ")
        file_content = read_file(file_path)

    use_search = input("Do you want to use search? (y/n): ").lower() == "y"
    return objective, file_content, use_search


def manage_tasks(objective, file_content, use_search):
    """Manage the orchestrator and sub-agent tasks."""
    task_exchanges = []
    gpt_tasks = []
    file_content_for_gpt = file_content

    while True:
        previous_results = [result for _, result in task_exchanges]

        if not task_exchanges:
            gpt_result, file_content_for_gpt, search_query = gpt_orchestrator(
                objective, file_content, previous_results, use_search
            )
        else:
            gpt_result, _, search_query = gpt_orchestrator(
                objective, previous_results=previous_results, use_search=use_search
            )

        if isinstance(gpt_result, str):
            if "The task is complete:" in gpt_result:
                return task_exchanges, gpt_result.replace("The task is complete:", "").strip()
            elif "No action required:" in gpt_result:
                return task_exchanges, gpt_result

            # Sub-agent execution
            sub_task_prompt = gpt_result
            if file_content_for_gpt and not gpt_tasks:
                sub_task_prompt = f"{sub_task_prompt}\n\nFile content:\n{file_content_for_gpt}"

            sub_task_result = gpt_sub_agent(
                sub_task_prompt, search_query, gpt_tasks, use_search
            )
            gpt_tasks.append({"task": sub_task_prompt, "result": sub_task_result})
            task_exchanges.append((sub_task_prompt, sub_task_result))
            file_content_for_gpt = None


def refine_results(objective, task_exchanges):
    """Refine the results from the task exchanges."""
    sub_task_results = [
        f"Orchestrator Prompt: {prompt}\nSub-agent Result: {result}"
        for prompt, result in task_exchanges
    ]

    sanitized_objective = re.sub(r"\W+", "_", objective)
    timestamp = datetime.now().strftime("%H-%M-%S")
    refined_output = anthropic_refine(objective, sub_task_results, timestamp, sanitized_objective)
    return refined_output, sanitized_objective, timestamp


def parse_refined_output(refined_output, sanitized_objective):
    """Parse the refined output to extract project name and folder structure."""
    project_name_match = re.search(r"Project Name: (.*)", refined_output)
    project_name = (
        project_name_match.group(1).strip() if project_name_match else sanitized_objective
    )

    folder_structure_match = re.search(
        r"<folder_structure>(.*?)</folder_structure>", refined_output, re.DOTALL
    )
    folder_structure = {}
    if folder_structure_match:
        json_string = folder_structure_match.group(1).strip()
        try:
            folder_structure = json.loads(json_string)
        except json.JSONDecodeError as e:
            console.print(
                Panel(
                    renderable=f"Error parsing JSON: {e}",
                    title="[bold red]JSON Parsing Error[/bold red]",
                    title_align="left",
                    border_style="red",
                )
            )
    return project_name, folder_structure


def create_project_files(project_name, folder_structure, refined_output):
    """Create the project folder structure and save files."""
    code_blocks = re.findall(
        r"Filename: (\S+)\s*```[\w]*\n(.*?)\n```", refined_output, re.DOTALL
    )
    create_folder_structure(project_name, folder_structure, code_blocks)


def save_exchange_log(objective, task_exchanges, refined_output, sanitized_objective, timestamp):
    """Save the exchange log to a file."""
    max_length = 25
    truncated_objective = (
        sanitized_objective[:max_length]
        if len(sanitized_objective) > max_length
        else sanitized_objective
    )

    filename = f"{timestamp}_{truncated_objective}.md"
    exchange_log = f"Objective: {objective}\n\n"
    exchange_log += "=" * 40 + " Task Breakdown " + "=" * 40 + "\n\n"

    for i, (prompt, result) in enumerate(task_exchanges, start=1):
        exchange_log += f"Task {i}:\nPrompt: {prompt}\nResult: {result}\n\n"

    exchange_log += "=" * 40 + " Refined Final Output " + "=" * 40 + "\n\n"
    exchange_log += refined_output

    with open(filename, "w", encoding="utf-8") as file:
        file.write(exchange_log)

    console.print(f"\n[bold]Refined Final output:[/bold]\n{refined_output}")
    print(f"\nFull exchange log saved to {filename}")


# Main Execution Flow
if __name__ == "__main__":
    objective, file_content, use_search = get_user_inputs()

    task_exchanges, final_output = manage_tasks(objective, file_content, use_search)

    refined_output, sanitized_objective, timestamp = refine_results(objective, task_exchanges)

    project_name, folder_structure = parse_refined_output(refined_output, sanitized_objective)

    create_project_files(project_name, folder_structure, refined_output)

    save_exchange_log(objective, task_exchanges, refined_output, sanitized_objective, timestamp)
