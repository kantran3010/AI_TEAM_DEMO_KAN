from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table

console = Console()

def print_banner():
    banner = Text()
    banner.append("🤖 AI MULTI-AGENT DEV TEAM\n", style="bold cyan")
    banner.append("1. Kịch bản (Product Owner)  ➜  2. Coder (Developer)  ➜  3. Tester (QA Automation)", style="italic green")
    console.print(Panel(banner, border_style="bright_blue", expand=False))

def print_step(agent_name: str, emoji: str, title: str, color: str = "cyan"):
    header = f"{emoji} [{color} bold][{agent_name}][/{color} bold] {title}"
    console.print(Panel(header, border_style=color))

def print_status(message: str, style: str = "bold yellow"):
    console.print(f"[{style}]➜ {message}[/{style}]")

def print_success(message: str):
    console.print(f"[bold green]✔ {message}[/bold green]")

def print_error(message: str):
    console.print(f"[bold red]✘ {message}[/bold red]")

def print_test_results(passed: int, failed: int, total: int, stdout: str):
    table = Table(title="Kết Quả Kiểm Thử (QA Automation Report)")
    table.add_column("Tổng Test", justify="center", style="cyan")
    table.add_column("Thành công (PASS)", justify="center", style="green")
    table.add_column("Thất bại (FAIL)", justify="center", style="red")
    table.add_column("Tỉ lệ", justify="center", style="magenta")

    rate = f"{(passed / total * 100):.1f}%" if total > 0 else "0%"
    table.add_row(str(total), str(passed), str(failed), rate)
    console.print(table)
