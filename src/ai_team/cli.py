import argparse
import sys
from pathlib import Path

# Fix Windows console UTF-8 output encoding
if sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from ai_team.config import Config
from ai_team.orchestrator import TeamOrchestrator
from ai_team.affiliate.orchestrator import AffiliateOrchestrator
from ai_team.utils import ui

def main():
    parser = argparse.ArgumentParser(description="AI Multi-Agent Team: Lập trình phần mềm & Affiliate Marketing")
    parser.add_argument("--mode", choices=["dev", "affiliate"], default=None, help="Chế độ hoạt động: 'dev' (code) hoặc 'affiliate' (marketing)")
    parser.add_argument("-p", "--prompt", type=str, help="Yêu cầu / Thông tin sản phẩm")
    parser.add_argument("-m", "--model", type=str, default=None, help="Mô hình LLM (mặc định lấy từ .env)")
    parser.add_argument("-w", "--workspace", type=str, default=None, help="Thư mục làm việc đầu ra")

    args = parser.parse_args()

    # Check API Key
    if not Config.validate_keys():
        ui.console.print("[bold red]⚠ Cảnh báo: Chưa tìm thấy API Key nào trong môi trường hoặc file .env![/bold red]")
        ui.console.print("Vui lòng mở file [yellow].env[/yellow] và điền ít nhất một API Key:")
        ui.console.print("  - [cyan]GEMINI_API_KEY=...[/cyan] (Khuyến nghị, lấy miễn phí tại Google AI Studio)")
        ui.console.print("  - [cyan]OPENAI_API_KEY=...[/cyan]")
        ui.console.print("  - [cyan]GROQ_API_KEY=...[/cyan]\n")

        proceed = input("Bạn có muốn tiếp tục chạy thử không? (y/n): ").strip().lower()
        if proceed != "y":
            sys.exit(0)

    mode = args.mode
    if not mode:
        ui.print_banner()
        ui.console.print("[bold yellow]Chọn Team AI bạn muốn sử dụng:[/bold yellow]")
        ui.console.print("  [1] 💻 [bold green]Team Dev[/bold green] (Lập trình: Kịch bản -> Viết Code -> Chạy Pytest kiểm thử)")
        ui.console.print("  [2] 🛍️ [bold magenta]Team Affiliate[/bold magenta] (Marketing: Nghiên cứu -> Kịch bản Video TikTok -> Threads/FB -> CTA)")
        
        choice = input("\nNhập lựa chọn của bạn (1 hoặc 2, mặc định là 2): ").strip()
        mode = "dev" if choice == "1" else "affiliate"

    workspace_dir = Path(args.workspace).resolve() if args.workspace else Config.WORKSPACE_DIR

    if mode == "affiliate":
        product_info = args.prompt
        if not product_info:
            try:
                product_info = input("\n📦 Nhập tên/mô tả hoặc link sản phẩm Affiliate: ").strip()
            except (KeyboardInterrupt, EOFError):
                print("\nĐã hủy.")
                sys.exit(0)

        if not product_info:
            ui.print_error("Thông tin sản phẩm không được để trống!")
            sys.exit(1)

        orchestrator = AffiliateOrchestrator(workspace_dir=workspace_dir, model=args.model)
        orchestrator.run_campaign(product_info)
    else:
        requirement = args.prompt
        if not requirement:
            try:
                requirement = input("\n📝 Nhập ý tưởng phần mềm bạn muốn Team AI phát triển: ").strip()
            except (KeyboardInterrupt, EOFError):
                print("\nĐã hủy.")
                sys.exit(0)

        if not requirement:
            ui.print_error("Yêu cầu không được để trống!")
            sys.exit(1)

        orchestrator = TeamOrchestrator(workspace_dir=workspace_dir, model=args.model)
        orchestrator.run_workflow(requirement)

if __name__ == "__main__":
    main()
