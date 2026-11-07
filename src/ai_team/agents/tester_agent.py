import subprocess
import sys
import re
from pathlib import Path
from typing import Optional, Dict, Tuple
from ai_team.agents.base import BaseAgent

TESTER_SYSTEM_PROMPT = """
Bạn là một Senior QA & Test Automation Engineer chuyên nghiệp.
Nhiệm vụ của bạn là:
1. Đọc tài liệu Đặc tả/Kịch bản & Toàn bộ mã nguồn do Developer viết.
2. Thiết kế và viết bộ kiểm thử tự động toàn diện bằng thư viện `pytest`.
3. Bao quát các trường hợp: Luồng chuẩn (Happy path), Trường hợp biên (Edge cases), Dữ liệu sai/lỗi (Exception handling).

Quy tắc bắt buộc:
- Viết file test độc lập, tự làm sạch (cleanup) mock/file tạm nếu có sử dụng I/O hoặc file.
- Định dạng xuất file:
  ### File: tests/test_<tên_module>.py
  ```python
  import pytest
  # mã kiểm thử
  ```
- Đảm bảo import đúng cấu trúc file của dự án.
"""

class TesterAgent(BaseAgent):
    def __init__(self, model: Optional[str] = None):
        super().__init__(
            name="QA Tester",
            role="Senior Test Automation Engineer",
            system_prompt=TESTER_SYSTEM_PROMPT,
            model=model,
        )

    def generate_tests(self, spec_content: str, code_files: Dict[str, str]) -> str:
        code_context = "\n\n".join([f"--- File: {fname} ---\n{content}" for fname, content in code_files.items()])

        prompt = f"""
Hãy viết bộ kiểm thử tự động hoàn chỉnh (sử dụng pytest) cho dự án này.

TÀI LIỆU ĐẶC TẢ & KỊCH BẢN:
\"\"\"{spec_content}\"\"\"

MÃ NGUỒN CỦA DEVELOPER:
\"\"\"{code_context}\"\"\"

Yêu cầu:
- Tạo các file test đặt trong thư mục `tests/` (ví dụ: `### File: tests/test_main.py`).
- Viết các test case rõ ràng, có assert chi tiết.
- Đảm bảo test đúng các tiêu chuẩn nghiệm thu trong bản đặc tả.
"""
        return self.think_and_act(prompt)

    def run_tests(self, project_dir: Path) -> Tuple[bool, int, int, int, str]:
        """
        Executes pytest inside the project directory.
        Returns: (is_passed, total_tests, passed_tests, failed_tests, stdout_output)
        """
        # Ensure project directory is in PYTHONPATH so imports work
        env = dict(sys.modules.get("os", {}).environ or {})
        python_path = str(project_dir.resolve())
        if "PYTHONPATH" in env:
            env["PYTHONPATH"] = f"{python_path};{env['PYTHONPATH']}"
        else:
            env["PYTHONPATH"] = python_path

        cmd = [sys.executable, "-m", "pytest", "-v", "--tb=short", str(project_dir / "tests")]

        result = subprocess.run(
            cmd,
            cwd=str(project_dir),
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=env,
        )

        output = result.stdout + "\n" + result.stderr
        is_passed = (result.returncode == 0)

        # Parse test statistics from pytest output
        passed = 0
        failed = 0
        total = 0

        # Match pattern: "1 passed", "2 failed", etc.
        m_passed = re.search(r"(\d+)\s+passed", output)
        if m_passed:
            passed = int(m_passed.group(1))

        m_failed = re.search(r"(\d+)\s+failed", output)
        if m_failed:
            failed = int(m_failed.group(1))

        m_errors = re.search(r"(\d+)\s+error", output)
        if m_errors:
            failed += int(m_errors.group(1))

        total = passed + failed
        if total == 0 and is_passed and "no tests ran" not in output:
            passed = 1
            total = 1

        return is_passed, total, passed, failed, output
