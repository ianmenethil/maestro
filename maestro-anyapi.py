import os
import re
from rich.console import Console
from rich.panel import Panel
from datetime import datetime
import json
from litellm import completion
from tavily import TavilyClient
from orchestrator import gpt_orchestrator
from sub_agent import gpt_sub_agent
from refiner import anthropic_refine
from file_utils import create_folder_structure, create_folders_and_files

# Set environment variables for API keys for the services you are using
os.environ["OPENAI_API_KEY"] = "YOUR OPENAI API KEY"
os.environ["ANTHROPIC_API_KEY"] = "YOUR ANTHROPIC API KEY"
os.environ["GEMINI_API_KEY"] = "YOUR GEMINI API KEY"

# Define the models to be used for each stage
ORCHESTRATOR_MODEL = "gemini/gemini-1.5-flash-latest"
SUB_AGENT_MODEL = "gemini/gemini-1.5-flash-latest"
REFINER_MODEL = "gemini/gemini-1.5-flash-latest"

# Initialize the Rich Console
console = Console()

def read_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    return content

# Get the objective from user input
objective = input("Please enter your objective: ")

# Ask the user if they want to provide a file path
provide_file = input("Do you want to provide a file path? (y/n): ").lower() == 'y'

if provide_file:
    file_path = input("Please enter the file path: ")
    if os.path.exists(file_path):
        file_content = read_file(file_path)
    else:
        print(f"File not found: {file_path}")
        file_content = None
else:
    file_content = None

# Ask the user if they want to use search
use_search = input("Do you want to use search? (y/n): ").lower() == 'y'

task_exchanges = []
gpt_tasks = []

while True:
    previous_results = [result for _, result in task_exchanges]
    if not task_exchanges:
        gpt_result, file_content_for_gpt, search_query = gpt_orchestrator(objective, file_content, previous_results, use_search)
    else:
        gpt_result, _, search_query = gpt_orchestrator(objective, previous_results=previous_results, use_search=use_search)

    if "The task is complete:" in gpt_result:
        final_output = gpt_result.replace("The task is complete:", "").strip()
        break
    else:
        sub_task_prompt = gpt_result
        if file_content_for_gpt and not gpt_tasks:
            sub_task_prompt = f"{sub_task_prompt}\n\nFile content:\n{file_content_for_gpt}"
        sub_task_result = gpt_sub_agent(sub_task_prompt, search_query, gpt_tasks, use_search)
        gpt_tasks.append({"task": sub_task_prompt, "result": sub_task_result})
        task_exchanges.append((sub_task_prompt, sub_task_result))
        file_content_for_gpt = None

# Include both orchestrator prompts and sub-agent results in sub-task results
sub_task_results = [f"Orchestrator Prompt: {prompt}\nSub-agent Result: {result}" for prompt, result in task_exchanges]

sanitized_objective = re.sub(r'\W+', '_', objective)
timestamp = datetime.now().strftime("%H-%M-%S")
refined_output = anthropic_refine(objective, sub_task_results, timestamp, sanitized_objective)

project_name_match = re.search(r'Project Name: (.*)', refined_output)
project_name = project_name_match.group(1).strip() if project_name_match else sanitized_objective

folder_structure_match = re.search(r'<folder_structure>(.*?)</folder_structure>', refined_output, re.DOTALL)
folder_structure = {}
if folder_structure_match:
    json_string = folder_structure_match.group(1).strip()
    try:
        folder_structure = json.loads(json_string)
    except json.JSONDecodeError as e:
        console.print(Panel(f"Error parsing JSON: {e}", title="[bold red]JSON Parsing Error[/bold red]", title_align="left", border_style="red"))
        console.print(Panel(f"Invalid JSON string: [bold]{json_string}[/bold]", title="[bold red]Invalid JSON String[/bold red]", title_align="left", border_style="red"))

# Ensure proper extraction of filenames and code contents
code_blocks = re.findall(r'Filename: (\S+)\s*```[\w]*\n(.*?)\n```', refined_output, re.DOTALL)
create_folder_structure(project_name, folder_structure, code_blocks)

max_length = 25
truncated_objective = sanitized_objective[:max_length] if len(sanitized_objective) > max_length else sanitized_objective

filename = f"{timestamp}_{truncated_objective}.md"

exchange_log = f"Objective: {objective}\n\n"
exchange_log += "=" * 40 + " Task Breakdown " + "=" * 40 + "\n\n"
for i, (prompt, result) in enumerate(task_exchanges, start=1):
    exchange_log += f"Task {i}:\n"
    exchange_log += f"Prompt: {prompt}\n"
    exchange_log += f"Result: {result}\n\n"

exchange_log += "=" * 40 + " Refined Final Output " + "=" * 40 + "\n\n"
exchange_log += refined_output

console.print(f"\n[bold]Refined Final output:[/bold]\n{refined_output}")

with open(filename, 'w') as file:
    file.write(exchange_log)
print(f"\nFull exchange log saved to {filename}")

