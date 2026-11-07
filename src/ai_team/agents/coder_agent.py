from ai_team.agents.base import BaseAgent
from typing import Optional, Dict

CODER_SYSTEM_PROMPT = """
Bạn là một Senior Full-Stack Python Developer với kỹ năng viết mã sạch (Clean Code), tối ưu và an toàn.
Nhiệm vụ của bạn là hiện thực hóa các yêu cầu và đặc tả kỹ thuật thành mã nguồn Python hoàn chỉnh.

Quy tắc bắt buộc:
1. Viết code đầy đủ, KHÔNG dùng placeholder như `pass`, `# TODO: implement this`, `# Code goes here`.
2. Phân chia module rõ ràng (mỗi file một trách nhiệm).
3. Sử dụng Type Hints chuẩn mực và xử lý ngoại lệ cẩn thận.
4. ĐỊNH DẠNG ĐẦU RA:
   Mỗi file phải được định dạng chính xác theo cú pháp sau để parser tự động lưu file:
   ### File: <tên_file.py>
   ```python
   # mã nguồn của file
   ```
   Ví dụ:
   ### File: models.py
   ```python
   from dataclasses import dataclass

   @dataclass
   class Task:
       id: int
       title: str
   ```
"""

class CoderAgent(BaseAgent):
    def __init__(self, model: Optional[str] = None):
        super().__init__(
            name="Developer",
            role="Senior Python Engineer",
            system_prompt=CODER_SYSTEM_PROMPT,
            model=model,
        )

    def generate_code(self, spec_content: str) -> str:
        prompt = f"""
Dựa trên tài liệu Kịch bản & Đặc tả kỹ thuật dưới đây, hãy lập trình toàn bộ mã nguồn của dự án:

TÀI LIỆU ĐẶC TẢ:
\"\"\"{spec_content}\"\"\"

Hãy tạo tất cả các file mã nguồn cần thiết (không bao gồm test file, vì Tester sẽ làm việc đó).
Hãy nhớ tuân thủ cú pháp:
### File: <tên_file.py>
```python
<nội dung code>
```
"""
        return self.think_and_act(prompt)

    def fix_code(self, spec_content: str, current_files: Dict[str, str], error_report: str) -> str:
        code_context = "\n\n".join([f"--- File: {fname} ---\n{content}" for fname, content in current_files.items()])

        prompt = f"""
Agent Kiểm thử (QA Tester) đã chạy kiểm thử và phát hiện các lỗi sau:

BÁO CÁO LỖI VÀ STACKTRACE:
\"\"\"{error_report}\"\"\"

CÁC FILE MÃ NGUỒN HIỆN TẠI:
\"\"\"{code_context}\"\"\"

YÊU CẦU:
1. Phân tích nguyên nhân gốc rễ gây ra lỗi trong báo cáo kiểm thử.
2. Sửa lại các file bị lỗi để toàn bộ test cases có thể vượt qua (PASS).
3. Chỉ cần cung cấp lại các file đã được sửa hoặc bổ sung theo đúng cú pháp:
### File: <tên_file.py>
```python
<code đã sửa hoàn chỉnh>
```
"""
        return self.think_and_act(prompt, context=spec_content)
