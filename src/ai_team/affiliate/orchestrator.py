import re
from pathlib import Path
from typing import Optional
from ai_team.config import Config
from ai_team.affiliate.agents.research_agent import AffiliateResearcherAgent
from ai_team.affiliate.agents.video_script_agent import VideoScriptAgent
from ai_team.affiliate.agents.social_copy_agent import SocialCopyAgent
from ai_team.affiliate.agents.visual_agent import VisualDesignerAgent
from ai_team.affiliate.agents.compliance_agent import ConversionComplianceAgent
from ai_team.utils import ui

class AffiliateOrchestrator:
    def __init__(self, workspace_dir: Optional[Path] = None, model: Optional[str] = None):
        self.base_dir = workspace_dir or Config.WORKSPACE_DIR
        self.model = model or Config.DEFAULT_MODEL

        # Initialize 5 specialized affiliate agents
        self.research_agent = AffiliateResearcherAgent(model=self.model)
        self.video_agent = VideoScriptAgent(model=self.model)
        self.social_agent = SocialCopyAgent(model=self.model)
        self.visual_agent = VisualDesignerAgent(model=self.model)
        self.compliance_agent = ConversionComplianceAgent(model=self.model)

    def _slugify(self, text: str) -> str:
        slug = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE).strip().lower()
        slug = re.sub(r"[-\s]+", "_", slug)
        return slug[:35] if slug else "affiliate_campaign"

    def run_campaign(self, product_info: str) -> Path:
        ui.console.print("\n")
        ui.print_banner()
        ui.console.print(f"[bold magenta]🛍️ SẢN PHẨM / CHIẾN DỊCH AFFILIATE:[/bold magenta] {product_info}\n")

        # Create output campaign directory
        product_slug = self._slugify(product_info.split("\n")[0])
        campaign_dir = self.base_dir / "affiliate" / product_slug
        campaign_dir.mkdir(parents=True, exist_ok=True)

        # -------------------------------------------------------------
        # BƯỚC 1: BOT NGHIÊN CỨU & TÌM GÓC TIẾP CẬN (RESEARCHER)
        # -------------------------------------------------------------
        ui.print_step("Bot 1: Market Researcher", "🕵️", "Đang đào sâu Insight, tìm USP và 5 góc tiếp cận...", "cyan")
        with ui.console.status("[bold cyan]Đang phân tích tâm lý khách hàng & tử huyệt cảm xúc..."):
            research_result = self.research_agent.analyze_product(product_info)

        file_research = campaign_dir / "01_research_and_angles.md"
        file_research.write_text(research_result, encoding="utf-8")
        ui.print_success(f"Đã lưu bản nghiên cứu: [underline]{file_research}[/underline]\n")

        # -------------------------------------------------------------
        # BƯỚC 2: BOT VIẾT KỊCH BẢN VIDEO NGẮN (TIKTOK/REELS/SHORTS)
        # -------------------------------------------------------------
        ui.print_step("Bot 2: Scriptwriter", "🎬", "Đang sáng tác 3 kịch bản video ngắn & Prompts AI Faceless...", "green")
        with ui.console.status("[bold green]Đang phân cảnh Visual/Audio/Hook 3 giây đầu..."):
            video_result = self.video_agent.write_scripts(research_result)

        file_video = campaign_dir / "02_short_video_scripts.md"
        file_video.write_text(video_result, encoding="utf-8")
        ui.print_success(f"Đã lưu kịch bản video ngắn: [underline]{file_video}[/underline]\n")

        # -------------------------------------------------------------
        # BƯỚC 3: BOT VIẾT BÀI CHỮ (THREADS, FACEBOOK GROUP, BLOG SEO)
        # -------------------------------------------------------------
        ui.print_step("Bot 3: Social Copywriter", "✍️", "Đang viết chuỗi Threads, bài Review Facebook và Blog SEO...", "yellow")
        with ui.console.status("[bold yellow]Đang soạn thảo nội dung đa kênh tự nhiên..."):
            social_result = self.social_agent.write_copy(research_result)

        file_social = campaign_dir / "03_social_and_seo_content.md"
        file_social.write_text(social_result, encoding="utf-8")
        ui.print_success(f"Đã lưu bài viết đa kênh: [underline]{file_social}[/underline]\n")

        # -------------------------------------------------------------
        # BƯỚC 4: BOT THIẾT KẾ HÌNH ẢNH SẢN PHẨM & AI PROMPTER (VISUAL CREATIVE)
        # -------------------------------------------------------------
        ui.print_step("Bot 4: Visual Creative Director", "🎨", "Đang thiết kế 5 concept hình ảnh giới thiệu & Prompts AI (Midjourney/Flux)...", "blue")
        with ui.console.status("[bold blue]Đang tạo mô tả mỹ thuật, góc chụp, bố cục và prompts tiếng Anh..."):
            visual_result = self.visual_agent.generate_image_prompts(product_info, research_result)

        file_visual = campaign_dir / "04_product_image_prompts.md"
        file_visual.write_text(visual_result, encoding="utf-8")
        ui.print_success(f"Đã lưu bộ mô tả & prompt hình ảnh: [underline]{file_visual}[/underline]\n")

        # -------------------------------------------------------------
        # BƯỚC 5: BOT KIỂM DUYỆT TỪ CẤM & TỐI ƯU CHUYỂN ĐỔI (COMPLIANCE)
        # -------------------------------------------------------------
        ui.print_step("Bot 5: Compliance & CRO", "🛡️", "Đang rà soát từ cấm sàn & tạo bộ CTA kích thích đơn hàng...", "magenta")
        with ui.console.status("[bold magenta]Đang kiểm tra chính sách TikTok/Facebook & tạo bộ Hashtags..."):
            summary_context = f"{research_result[:1000]}\n...\n{video_result[:1000]}"
            compliance_result = self.compliance_agent.optimize_campaign(product_info, summary_context)

        file_compliance = campaign_dir / "05_compliance_and_cta.md"
        file_compliance.write_text(compliance_result, encoding="utf-8")
        ui.print_success(f"Đã lưu báo cáo kiểm duyệt & CTA: [underline]{file_compliance}[/underline]\n")

        # -------------------------------------------------------------
        # TỔNG HỢP GÓI CHIẾN DỊCH HOÀN CHỈNH (ALL-IN-ONE PACKAGE)
        # -------------------------------------------------------------
        all_in_one_file = campaign_dir / "ALL_IN_ONE_AFFILIATE_PACKAGE.md"
        package_content = f"""# 🚀 TRỌN BỘ CHIẾN DỊCH AFFILIATE MARKETING HOÀN CHỈNH

## 📌 Sản Phẩm Mục Tiêu:
{product_info}

---

## 1. 🕵️ NGHIÊN CỨU SẢN PHẨM & 5 GÓC TIẾP CẬN TRIỆU VIEW
{research_result}

---

## 2. 🎬 3 KỊCH BẢN VIDEO NGẮN (TIKTOK / REELS / SHORTS) + AI PROMPTS
{video_result}

---

## 3. ✍️ BÀI VIẾT ĐA KÊNH (THREADS VIRAL, FACEBOOK GROUP, BLOG SEO)
{social_result}

---

## 4. 🎨 BỘ MÔ TẢ & PROMPTS TẠO HÌNH ẢNH GIỚI THIỆU SẢN PHẨM (AI VISUAL SHOWCASE)
{visual_result}

---

## 5. 🛡️ BÁO CÁO TỪ CẤM, BỘ CTA KÉO ĐƠN & HASHTAG CHIẾN LƯỢC
{compliance_result}
"""
        all_in_one_file.write_text(package_content, encoding="utf-8")
        ui.console.print()
        ui.print_success(f"🎉 HOÀN TẤT TOÀN BỘ CHIẾN DỊCH!")
        ui.console.print(f"[bold green]📦 File gói tổng hợp sẵn sàng sử dụng:[/bold green] [underline]{all_in_one_file}[/underline]\n")

        return campaign_dir
