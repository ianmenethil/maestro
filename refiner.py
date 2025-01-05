from rich.console import Console
from rich.panel import Panel
import re
import json

# Initialize the Rich Console
console = Console()

def calculate_subagent_cost(model, input_tokens, output_tokens):
    # Pricing information per model
    pricing = {
        "claude-3-opus-20240229": {"input_cost_per_mtok": 15.00, "output_cost_per_mtok": 75.00},
        "claude-3-haiku-20240307": {"input_cost_per_mtok": 0.25, "output_cost_per_mtok": 1.25},
        "claude-3-sonnet-20240229": {"input_cost_per_mtok": 3.00, "output_cost_per_mtok": 15.00},
    }

    # Calculate cost
    input_cost = (input_tokens / 1_000_000) * pricing[model]["input_cost_per_mtok"]
    output_cost = (output_tokens / 1_000_000) * pricing[model]["output_cost_per_mtok"]
    total_cost = input_cost + output_cost

    return total_cost

def anthropic_refine(objective, sub_task_results, filename, projectname, continuation=False):
    console.print("\nCalling Opus to provide the refined final output for your objective:")
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Objective: " + objective + "\n\nSub-task results:\n" + "\n".join(sub_task_results) + "\n\nPlease review and refine the sub-task results into a cohesive final output. Add any missing information or details as needed. When working on code projects, ONLY AND ONLY IF THE PROJECT IS CLEARLY A CODING ONE please provide the following:\n1. Project Name: Create a concise and appropriate project name that fits the project based on what it's creating. The project name should be no more than 20 characters long.\n2. Folder Structure: Provide the folder structure as a valid JSON object, where each key represents a folder or file, and nested keys represent subfolders. Use null values for files. Ensure the JSON is properly formatted without any syntax errors. Please make sure all keys are enclosed in double quotes, and ensure objects are correctly encapsulated with braces, separating items with commas as necessary.\nWrap the JSON object in <folder_structure> tags.\n3. Code Files: For each code file, include ONLY the file name NEVER EVER USE THE FILE PATH OR ANY OTHER FORMATTING YOU ONLY USE THE FOLLOWING format 'Filename: <filename>' followed by the code block enclosed in triple backticks, with the language identifier after the opening backticks, like this:\n\n```python\n<code>\n```"}
            ]
        }
    ]

    opus_response = anthropic_client.messages.create(
        model=REFINER_MODEL,
        max_tokens=4096,
        messages=messages
    )

    response_text = opus_response.content[0].text.strip()
    console.print(f"Input Tokens: {opus_response.usage.input_tokens}, Output Tokens: {opus_response.usage.output_tokens}")
    total_cost = calculate_subagent_cost(REFINER_MODEL, opus_response.usage.input_tokens, opus_response.usage.output_tokens)
    console.print(f"Refine Cost: ${total_cost:.4f}")

    if opus_response.usage.output_tokens >= 4000 and not continuation:  # Threshold set to 4000 as a precaution
        console.print("[bold yellow]Warning:[/bold yellow] Output may be truncated. Attempting to continue the response.")
        continuation_response_text = anthropic_refine(objective, sub_task_results + [response_text], filename, projectname, continuation=True)
        response_text += "\n" + continuation_response_text

    console.print(Panel(response_text, title="[bold green]Final Output[/bold green]", title_align="left", border_style="green"))
    return response_text
