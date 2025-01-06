# F:\_AI\MCPServer\maestro\refactored\file_utils.py
import os
from typing import Dict, List, Tuple
from rich.console import Console
from rich.panel import Panel
import pathlib

# Initialize the Rich Console
console = Console()


def read_file(file_path: str) -> str:
    """Read file with validation and error handling."""
    try:
        path = pathlib.Path(file_path).resolve()
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(path, "r", encoding="utf-8") as file:
            return file.read()
    except Exception as e:
        raise IOError(f"Error reading file {file_path}: {str(e)}") from e


def create_folder_structure(
    project_name: str,
    folder_structure: Dict,
    code_blocks: List[Tuple[str, str]]
) -> None:
    """Create project folder structure with validation."""
    try:
        project_path = pathlib.Path(project_name).resolve()
        os.makedirs(project_path, exist_ok=True)
        console.print(
            Panel(
                f"Created project folder: [bold]{project_path}[/bold]",
                title="[bold green]Project Folder[/bold green]",
                title_align="left",
                border_style="green",
            )
        )
    except OSError as e:
        console.print(
            Panel(
                f"Error creating project folder: [bold]{project_path}[/bold]\nError: {e}",
                title="[bold red]Project Folder Creation Error[/bold red]",
                title_align="left",
                border_style="red",
            )
        )
        return

    create_folders_and_files(str(project_path), folder_structure, code_blocks)


def create_folders_and_files(
    current_path: str,
    structure: Dict,
    code_blocks: List[Tuple[str, str]]
) -> None:
    """Recursively create folders and files from structure definition."""
    for key, value in structure.items():
        path = os.path.join(current_path, key)
        if isinstance(value, dict):
            try:
                os.makedirs(path, exist_ok=True)
                console.print(
                    Panel(
                        f"Created folder: [bold]{path}[/bold]",
                        title="[bold blue]Folder Creation[/bold blue]",
                        title_align="left",
                        border_style="blue",
                    )
                )
                create_folders_and_files(path, value, code_blocks)
            except OSError as e:
                console.print(
                    Panel(
                        f"Error creating folder: [bold]{path}[/bold]\nError: {e}",
                        title="[bold red]Folder Creation Error[/bold red]",
                        title_align="left",
                        border_style="red",
                    )
                )
        else:
            code_content = next(
                (code for file, code in code_blocks if file == key), None
            )
            if code_content:
                try:
                    with open(path, "w", encoding="utf-8") as file:
                        file.write(code_content)
                    console.print(
                        Panel(
                            f"Created file: [bold]{path}[/bold]",
                            title="[bold green]File Creation[/bold green]",
                            title_align="left",
                            border_style="green",
                        )
                    )
                except IOError as e:
                    console.print(
                        Panel(
                            f"Error creating file: [bold]{path}[/bold]\nError: {e}",
                            title="[bold red]File Creation Error[/bold red]",
                            title_align="left",
                            border_style="red",
                        )
                    )
            else:
                console.print(
                    Panel(
                        f"Code content not found for file: [bold]{key}[/bold]",
                        title="[bold yellow]Missing Code Content[/bold yellow]",
                        title_align="left",
                        border_style="yellow",
                    )
                )
