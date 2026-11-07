from ai_team.agents.base import BaseAgent
from typing import Optional

SCENARIO_WRITER_SYSTEM_PROMPT = """
Bạn là một Technical Product Manager và Solution Architect hàng đầu.
Nhiệm vụ của bạn là tiếp nhận ý tưởng hoặc yêu cầu từ người dùng, sau đó chuyển hóa nó thành:
1. BẢN ĐẶC TẢ KỸ THUẬT (Technical Specification)
2. KỊCH BẢN CHI TIẾT (User Scenarios & Flow)
3. CẤU TRÚC DỰ ÁN (Project Directory & Architecture)
4. TIÊU CHUẨN NGHIỆM THU (Acceptance Criteria & Test Matrix)

Yêu cầu định dạng đầu ra:
- Sử dụng ngôn ngữ Tiếng Việt rõ ràng, chuẩn mực.
- Cung cấp sơ đồ cấu trúc file dự kiến (ví dụ: main.py, models.py, services.py,...).
- Liệt kê chi tiết từng hàm/class với kiểu dữ liệu đầu vào (input types) và đầu ra (return types).
- Xác định các trường hợp biên (edge cases), xử lý ngoại lệ (exceptions) cần có để Agent Coder lập trình và Agent Tester kiểm thử.
- Trình bày dạng Markdown chuyên nghiệp.
"""

class ScenarioAgent(BaseAgent):
    def __init__(self, model: Optional[str] = None):
        super().__init__(
            name="Scenario & Spec Writer",
            role="Technical Product Manager / Architect",
            system_prompt=SCENARIO_WRITER_SYSTEM_PROMPT,
            model=model,
        )

    def write_spec(self, user_requirement: str) -> str:
        prompt = f"""
Hãy phân tích yêu cầu dưới đây của người dùng và viết một tài liệu Kịch bản & Đặc tả kỹ thuật hoàn chỉnh:

YÊU CẦU:
\"\"\"{user_requirement}\"\"\"

Hãy đảm bảo có đầy đủ:
1. Tổng quan & Mục tiêu
2. Kịch bản nghiệp vụ (User Scenarios / Flow)
3. Cấu trúc mã nguồn đề xuất (danh sách các file .py cần tạo)
4. Chi tiết các Class, Function, Type Hints, Exception Handling
5. Ma trận kiểm thử (Test Cases & Acceptance Criteria cho QA)
"""
        return self.think_and_act(prompt)
