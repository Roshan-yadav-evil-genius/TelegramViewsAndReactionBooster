from rich.console import Console
from rich.table import Table
from rich import box
from rich.panel import Panel
from rich.text import Text
import time

def create_table():
    table = Table(title="[bold yellow]My Colorful Table[/bold yellow]", 
                  show_header=True, header_style="bold", expand=True, 
                  border_style="bold purple", box=box.HEAVY)
    
    table.add_column("Post", header_style="bold red")
    table.add_column("Requested", header_style="bold green")
    table.add_column("Required", header_style="bold cyan")
    return table

def add_colored_row(table, col1_data, col2_data, col3_data, light=False):
    color_format = "bold" if not light else "dim"
    table.add_row(f"[{color_format} red]{col1_data}[/{color_format} red]", 
                  f"[{color_format} green]{col2_data}[/{color_format} green]", 
                  f"[{color_format} cyan]{col3_data}[/{color_format} cyan]")

def create_info_panel(counter):
    info_text = Text()
    info_text.append("Counter: ", style="bold blue")
    info_text.append(f"{counter}", style="bold red")
    info_text.append("\tStatus: ", style="bold blue")
    info_text.append("Active", style="bold green")
    info_text.append("\t\tMode: ", style="bold blue")
    info_text.append("Demo", style="bold yellow")

    panel = Panel(info_text, title="[bold magenta]Additional Information[/bold magenta]", expand=True)
    return panel

console = Console()
counter = 0

while True:
    table = create_table()
    
    # Updating rows with new values
    add_colored_row(table, f"Row {counter + 1}, Col 1", f"Row {counter + 1}, Col 2", f"Row {counter + 1}, Col 3", light=False)
    add_colored_row(table, f"Row {counter + 2}, Col 1", f"Row {counter + 2}, Col 2", f"Row {counter + 2}, Col 3", light=True)
    add_colored_row(table, f"Row {counter + 3}, Col 1", f"Row {counter + 3}, Col 2", f"Row {counter + 3}, Col 3", light=False)

    # Create and display the information panel
    info_panel = create_info_panel(counter)
    console.print(info_panel)
    console.print(table)
    
    time.sleep(1)
    console.clear()
    counter += 1
