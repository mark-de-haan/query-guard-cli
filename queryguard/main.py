from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from typer import Context, Exit, Option, Typer

from google.cloud.bigquery import Client as BigQueryClient

from .analysis import ForensicAuditor
from .client import fetch_recent_jobs, get_bq_client
from .console_utils import print_audit_results

app: Typer = Typer()
console: Console = Console()


@app.callback(invoke_without_command=True)
def main_callback(ctx: Context):
    """
    QueryGuard CLI - Audit BigQuery spend and find cost anomalies.
    """
    if ctx.invoked_subcommand is None:
        console.print(Panel(
            "[bold]QueryGuard CLI[/bold]\n\n"
            "The forensic auditor for your BigQuery bills.\n\n"
            "Usage:\n"
            "  [cyan]bqg scan[/cyan]    Start a forensic audit\n"
            "  [cyan]bqg scan --help[/cyan]  Show all options",
            title="Welcome",
            border_style="blue"
        ))
        raise Exit()


@app.command("scan")
def scan(
    project_id: str = Option(None, "--project", "-p", help="GCP Project ID. Defaults to local config."),
    region: str = Option("us", "--region", "-r", help="BigQuery Region (e.g. us, eu, europe-west4)."),
    days: int = Option(7, "--days", "-d", help="Lookback window in days."),
    global_scan: bool = Option(False, "--global", "-g", help="Auto-discover and scan all active regions."),
    limit: int = Option(10, "--limit", "-l", help="Number of queries to show."),
    humans_only: bool = Option(False, "--humans-only", help="Filter out service accounts and bots."),
):
    """
    Audit BigQuery spend. Use --humans-only to find manual errors.
    """

    client: BigQueryClient = get_bq_client(project_id)
    target_project_id: str = client.project

    region_display = "GLOBAL (Auto-Discovery)" if global_scan else region
    
    console.print(f"[bold]QueryGuard Forensic Scan[/bold]")
    console.print(f"Target: [cyan]{target_project_id}[/cyan] | Region: [cyan]{region_display}[/cyan] | Lookback: [cyan]{days} days[/cyan]\n")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description="Scanning audit logs...", total=None)
        rows = fetch_recent_jobs(client, target_project_id, region, days, global_scan, limit=limit * 5)
        jobs = list(rows)

    if not jobs:
        console.print("[yellow]No billed queries found in the specified period.[/yellow]")
        raise Exit()

    # 3. Build Table
    table: Table = Table(
        title=f"Top Expensive Queries ({'Humans Only' if humans_only else 'All Users'})", 
        border_style="white", 
        box=None, 
        header_style="bold cyan"
    )

    table.add_column("User", style="white", no_wrap=True)
    table.add_column("Region", justify="right")
    table.add_column("Data", justify="right")
    table.add_column("Cost", justify="right", style="green")
    table.add_column("Flags", style="red")
    table.add_column("Query Snippet", style="dim")

    displayed_count: float = 0
    total_spend: float = 0.0

    job: dict
    for job in jobs:
        sql = job.get('query') or "" 
        user_email = job.get('user_email') or "unknown"
        total_bytes_billed = job.get('total_bytes_billed') or 0
        job_region: str = job.get('region') or "us"

        if humans_only:
            # Common patterns for bots/service accounts
            if "gserviceaccount" in user_email or "monitoring" in user_email:
                continue

        # FIXME calculate more precise region if global scan
        cost: float = ForensicAuditor.calculate_cost(total_bytes_billed, job_region)
        total_spend += cost
        risks: list[str] = ForensicAuditor.analyze_query(sql, total_bytes_billed)
        
        gb_scanned: float = total_bytes_billed / (1024**3)
        
        clean_query: str = " ".join(sql.replace("\n", " ").split())
        query_snippet: str = clean_query[:60] + "..." if len(clean_query) > 60 else clean_query

        table.add_row(
            user_email.split('@')[0], 
            job_region,
            f"{gb_scanned:.2f} GB",
            f"${cost:.2f}",
            ", ".join(risks) if risks else "[dim]OK[/dim]",
            query_snippet
        )

        displayed_count += 1
        if displayed_count >= limit:
            break

    print_audit_results(console, table, total_spend, displayed_count)
    


if __name__ == "__main__":
    app()