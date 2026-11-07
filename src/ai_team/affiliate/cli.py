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
from ai_team.affiliate.orchestrator import AffiliateOrchestrator
from ai_team.utils import ui

def main():
    parser = argparse.ArgumentParser(description="Affiliate Multi-Agent Bot Team: Video ngắn + Threads/Facebook + Tối ưu chuyển đổi")
    parser.add_argument("-p", "--product", type=str, help="Tên sản phẩm, tính năng nổi bật hoặc link sản phẩm")
    parser.add_argument("-m", "--model", type=str, default=None, help="Mô hình LLM (mặc định lấy từ .env)")
    parser.add_argument("-w", "--workspace", type=str, default=None, help="Thư mục lưu trữ chiến dịch")

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

    product_info = args.product
    if not product_info:
        ui.print_banner()
        ui.console.print("[bold cyan]🛍️ CHÀO MỪNG BẠN ĐẾN VỚI TEAM BOT AI AFFILIATE MARKETING![/bold cyan]")
        ui.console.print("Hệ thống sẽ tự động tạo: [green]Kịch bản TikTok/Reels[/green] + [yellow]Threads/Facebook[/yellow] + [blue]Mô tả hình ảnh AI (Midjourney/Flux)[/blue] + [magenta]SEO & CTA[/magenta]\n")
        try:
            product_info = input("📦 Nhập tên/mô tả sản phẩm (hoặc dán link sản phẩm affiliate): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nĐã hủy.")
            sys.exit(0)

    if not product_info:
        ui.print_error("Thông tin sản phẩm không được để trống!")
        sys.exit(1)

    workspace_dir = Path(args.workspace).resolve() if args.workspace else Config.WORKSPACE_DIR
    orchestrator = AffiliateOrchestrator(workspace_dir=workspace_dir, model=args.model)
    orchestrator.run_campaign(product_info)

if __name__ == "__main__":
    main()
