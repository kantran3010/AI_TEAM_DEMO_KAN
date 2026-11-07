import time
from pathlib import Path
from typing import Dict, Optional
from ai_team.config import Config
from ai_team.agents.scenario_agent import ScenarioAgent
from ai_team.agents.coder_agent import CoderAgent
from ai_team.agents.tester_agent import TesterAgent
from ai_team.utils.file_extractor import FileExtractor
from ai_team.utils import ui

class TeamOrchestrator:
    def __init__(self, workspace_dir: Optional[Path] = None, model: Optional[str] = None):
        self.workspace_dir = workspace_dir or Config.WORKSPACE_DIR
        self.project_dir = self.workspace_dir / "project"
        self.model = model or Config.DEFAULT_MODEL
        
        # Initialize agents
        self.scenario_agent = ScenarioAgent(model=self.model)
        self.coder_agent = CoderAgent(model=self.model)
        self.tester_agent = TesterAgent(model=self.model)

    def run_workflow(self, user_requirement: str) -> bool:
        ui.print_banner()
        ui.console.print(f"[bold cyan]🎯 Yêu cầu dự án:[/bold cyan] {user_requirement}\n")

        # 0. Setup workspace
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        self.project_dir.mkdir(parents=True, exist_ok=True)

        # -------------------------------------------------------------
        # BƯỚC 1: AGENT KỊCH BẢN (PRODUCT OWNER / ARCHITECT)
        # -------------------------------------------------------------
        ui.print_step("Agent 1: Kịch bản", "📝", "Đang phân tích yêu cầu và viết kịch bản đặc tả...", "cyan")
        with ui.console.status("[bold cyan]Đang tạo tài liệu đặc tả & tiêu chuẩn nghiệm thu..."):
            spec_content = self.scenario_agent.write_spec(user_requirement)
        
        spec_path = self.workspace_dir / "1_spec_scenario.md"
        spec_path.write_text(spec_content, encoding="utf-8")
        ui.print_success(f"Đã hoàn thành kịch bản & đặc tả: [underline]{spec_path}[/underline]\n")

        # -------------------------------------------------------------
        # BƯỚC 2: AGENT LẬP TRÌNH (DEVELOPER / CODER)
        # -------------------------------------------------------------
        ui.print_step("Agent 2: Coder", "💻", "Đang hiện thực hóa mã nguồn từ bản đặc tả...", "green")
        with ui.console.status("[bold green]Đang lập trình các module..."):
            raw_code = self.coder_agent.generate_code(spec_content)
        
        code_files = FileExtractor.extract_files(raw_code)
        if not code_files:
            ui.print_error("Không tìm thấy định dạng file hợp lệ từ Coder! Đang thử lưu dưới dạng main.py...")
            code_files = {"main.py": raw_code}

        saved_code_files = FileExtractor.save_files(code_files, self.project_dir)
        for f in saved_code_files:
            ui.print_success(f"Đã tạo file mã nguồn: [bold]{f.name}[/bold]")
        ui.console.print()

        # -------------------------------------------------------------
        # BƯỚC 3: AGENT KIỂM THỬ (QA AUTOMATION TESTER)
        # -------------------------------------------------------------
        ui.print_step("Agent 3: QA Tester", "🧪", "Đang viết bộ kiểm thử tự động (pytest)...", "yellow")
        
        # Load current code files for tester
        current_code_files = self._get_current_source_files()
        with ui.console.status("[bold yellow]Đang sinh các test cases..."):
            raw_tests = self.tester_agent.generate_tests(spec_content, current_code_files)
        
        test_files = FileExtractor.extract_files(raw_tests)
        if not test_files:
            test_files = {"tests/test_main.py": raw_tests}

        saved_tests = FileExtractor.save_files(test_files, self.project_dir)
        for t in saved_tests:
            ui.print_success(f"Đã tạo file kiểm thử: [bold]{t.name}[/bold]")
        ui.console.print()

        # -------------------------------------------------------------
        # BƯỚC 4: THỰC THI KIỂM THỬ & VÒNG LẶP TỰ ĐỘNG SỬA LỖI (SELF-HEALING)
        # -------------------------------------------------------------
        ui.print_step("QA & CI/CD", "⚙️", "Đang thực thi bộ kiểm thử tự động...", "magenta")
        
        round_count = 0
        max_rounds = Config.MAX_RETRY_ROUNDS
        is_passed = False

        while round_count <= max_rounds:
            round_count += 1
            ui.print_status(f"Lần kiểm thử #{round_count}...", style="bold magenta")
            
            passed, total, pass_cnt, fail_cnt, test_output = self.tester_agent.run_tests(self.project_dir)
            ui.print_test_results(pass_cnt, fail_cnt, total, test_output)

            if passed:
                is_passed = True
                ui.print_success("🎉 TUYỆT VỜI! Tất cả các bài kiểm thử đã vượt qua thành công (100% PASS)!")
                break
            
            if round_count > max_rounds:
                ui.print_error(f"Đã đạt số lần sửa tối đa ({max_rounds}). Một số bài kiểm thử vẫn chưa vượt qua.")
                break

            # Feedback loop to Coder
            ui.print_step("Phản Hồi Lỗi (Bug Loop)", "🔄", f"Phát hiện lỗi! Gửi bug report cho Coder sửa lại lần #{round_count}...", "red")
            current_code_files = self._get_current_source_files()
            
            with ui.console.status("[bold red]Coder đang phân tích lỗi và vá code..."):
                fixed_code_raw = self.coder_agent.fix_code(spec_content, current_code_files, test_output)
            
            fixed_files = FileExtractor.extract_files(fixed_code_raw)
            if fixed_files:
                FileExtractor.save_files(fixed_files, self.project_dir)
                for f_name in fixed_files.keys():
                    ui.print_success(f"Coder đã sửa và cập nhật: [bold]{f_name}[/bold]")
            else:
                ui.print_status("Coder không sửa thêm file nào hoặc không parse được file.")
            
            ui.console.print()

        # -------------------------------------------------------------
        # TỔNG KẾT
        # -------------------------------------------------------------
        self._generate_summary_report(is_passed, user_requirement)
        return is_passed

    def _get_current_source_files(self) -> Dict[str, str]:
        files = {}
        for path in self.project_dir.rglob("*.py"):
            # Exclude tests folder from source code context
            if "tests" in path.parts:
                continue
            rel_name = path.relative_to(self.project_dir).as_posix()
            files[rel_name] = path.read_text(encoding="utf-8")
        return files

    def _generate_summary_report(self, is_passed: bool, requirement: str):
        summary_path = self.workspace_dir / "SUMMARY.md"
        status_text = "Thành công (All Tests Passed)" if is_passed else "Hoàn thành một phần (Cần kiểm tra thêm)"
        
        files_list = []
        for path in self.project_dir.rglob("*.py"):
            files_list.append(f"- `{path.relative_to(self.project_dir).as_posix()}`")
        files_text = "\n".join(files_list)

        content = f"""# Báo Cáo Kết Quả AI Dev Team

## 📌 Yêu Cầu Dự Án:
{requirement}

## 📊 Trạng Thái Dự Án:
**{status_text}**

## 📁 Danh Sách File Đã Tạo Trong `workspace/project/`:
{files_text}

## 🚀 Hướng Dẫn Chạy Sản Phẩm:
1. Di chuyển vào thư mục code:
   ```bash
   cd workspace/project
   ```
2. Chạy thử nghiệm với pytest:
   ```bash
   pytest -v tests/
   ```
3. Chạy ứng dụng:
   ```bash
   python main.py
   ```
"""
        summary_path.write_text(content, encoding="utf-8")
        ui.console.print(f"\n[bold green]📄 Đã xuất báo cáo tổng kết tại:[/bold green] [underline]{summary_path}[/underline]\n")
