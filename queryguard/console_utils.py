from rich.console import Console
from rich.panel import Panel
from rich.table import Table


def print_audit_results(
    console: Console,
    table: Table,
    total_spend: float,
    displayed_count: int
) -> None:
    """Prints the audit results in a formatted table."""
    console.print(table)
    console.print(Panel(
        f"[bold]Total Cost in View: ${total_spend:.2f}[/bold]\n"
        f"Showing {displayed_count} queries.",
        title="Audit Summary",
        border_style="white",
        expand=False
    ))
