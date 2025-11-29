# run.py
"""
Terminal UI for the Dining Hall Assistant.
Uses rich for formatting and your langgraph pipeline (build_graph from graph.py).
Run: python run.py
"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt
from rich.markdown import Markdown
from rich.text import Text
import sys
import time

console = Console()
MEAL_OPTIONS = [
    ("breakfast", "07:00 - 10:00"),
    ("lunch", "12:00 - 15:00"),
    ("evening_snacks", "16:00 - 18:00"),
    ("dinner", "19:00 - 22:00"),
    ("midnight_mess", "23:00 - 02:00"),
]

# Try to import your graph builder
try:
    from graph import build_graph
except Exception as e:
    console.print("[red]Error:[/red] could not import build_graph from graph.py")
    console.print(str(e))
    sys.exit(1)

# Build graph once (this may call embeddings & llm when invoked)
graph = build_graph()

def show_header():
    header = Text("Dining Hall AI Assistant", style="bold white on blue")
    console.rule()
    console.print(Panel(header, expand=False), justify="center")
    console.print("\nThis tool uses the college dining menu and an LLM to answer questions.")
    console.print("Select a meal or ask a custom question. (Press Ctrl+C to exit)\n")

def show_menu():
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("No.", justify="center")
    table.add_column("Meal Slot", justify="left")
    table.add_column("Time", justify="center")
    for i, (key, times) in enumerate(MEAL_OPTIONS, start=1):
        table.add_row(str(i), key, times)
    table.add_row(str(len(MEAL_OPTIONS)+1), "Custom question", "-")
    table.add_row(str(len(MEAL_OPTIONS)+2), "Exit", "-")
    console.print(table)

def query_graph(question: str):
    """
    Invoke the graph and return (context, answer) strings.
    """
    try:
        result = graph.invoke({"question": question})
    except Exception as e:
        # show helpful error
        return None, f"[Error invoking graph] {e}"
    ctx = result.get("context", "")
    ans = result.get("answer", "")
    return ctx, ans

def pretty_print_result(question: str, context: str, answer: str):
    console.rule("[bold green]Result[/bold green]")
    console.print(Panel(Text(question, style="bold"), title="Question"))

    console.print(Panel(Markdown(f"**Retrieved Context:**\n\n{context}"), title="Context", subtitle="RAG output", padding=(1,1)))

    # Answer panel
    console.print(Panel(Markdown(answer), title="Assistant Answer", subtitle="Friendly response", padding=(1,1)))

    # Optionally save to file
    save = Prompt.ask("Save this result to a file? (y/n)", choices=["y","n"], default="n")
    if save == "y":
        timestamp = int(time.time())
        fname = f"result_{timestamp}.txt"
        with open(fname, "w", encoding="utf-8") as f:
            f.write("Question:\n")
            f.write(question + "\n\n")
            f.write("Context:\n")
            f.write(context + "\n\n")
            f.write("Answer:\n")
            f.write(answer + "\n")
        console.print(f"[green]Saved to {fname}[/green]")

def main_loop():
    show_header()
    while True:
        show_menu()
        try:
            choice = IntPrompt.ask("Enter choice number", default=1)
        except KeyboardInterrupt:
            console.print("\n[bold yellow]Goodbye![/bold yellow]")
            break

        max_opt = len(MEAL_OPTIONS) + 2
        if not (1 <= choice <= max_opt):
            console.print("[red]Invalid choice. Try again.[/red]")
            continue

        if choice == max_opt:  # Exit
            console.print("\n[bold yellow]Exiting. Have a good day![/bold yellow]")
            break
        elif choice == len(MEAL_OPTIONS) + 1:  # custom question
            q = Prompt.ask("Type your question (e.g., 'Which dinner items are vegetarian?')")
            if not q.strip():
                console.print("[red]Empty question. Try again.[/red]")
                continue
            console.print("[cyan]Querying assistant...[/cyan]")
            ctx, ans = query_graph(q)
            if ctx is None:
                console.print(f"[red]{ans}[/red]")
            else:
                pretty_print_result(q, ctx, ans)
        else:
            meal_key = MEAL_OPTIONS[choice-1][0]
            q = f"What is available for {meal_key}?"
            console.print(f"[cyan]Querying assistant for {meal_key}...[/cyan]")
            ctx, ans = query_graph(q)
            if ctx is None:
                console.print(f"[red]{ans}[/red]")
            else:
                pretty_print_result(q, ctx, ans)

if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Interrupted. Bye![/bold yellow]")
