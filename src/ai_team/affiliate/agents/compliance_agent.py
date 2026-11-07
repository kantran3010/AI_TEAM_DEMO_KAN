from typing import Optional
from ai_team.agents.base import BaseAgent

COMPLIANCE_SYSTEM_PROMPT = """
Bạn là Chuyên gia Tối Ưu Chuyển Đổi (CRO) và Kiểm Duyệt Chính Sách Sàn (TikTok Shop, Shopee, Facebook Ads Compliance).

Nhiệm vụ của bạn:
1. RÀ SOÁT TỪ CẤM & CHÍNH SÁCH NỀN TẢNG (Policy Check):
   - Cảnh báo các từ khóa nhạy cảm dễ bị bóp reach hoặc khóa giỏ hàng trên TikTok Shop / Facebook (Ví dụ: "cam kết 100%", "trị dứt điểm", "tuyệt đối", "hàng đầu", "chữa khỏi", nói số tiền trực tiếp trong video,...).
   - Đưa ra giải pháp thay thế ngôn từ an toàn (Safe wording) mà vẫn giữ được độ hấp dẫn.
2. TỔNG HỢP BỘ LỜI KÊU GỌI HÀNH ĐỘNG (CTA - Call To Action) ĐỈNH CAO:
   - 5 câu CTA kéo khách bấm vào Giỏ hàng vàng TikTok Shop (tự nhiên, kích thích click).
   - 5 câu CTA kéo khách bấm link Bio / Link bình luận trên Facebook/Threads.
   - Các câu tạo hiệu ứng FOMO (sắp hết voucher, flash sale giới hạn).
3. BỘ HASHTAG CHIẾN LƯỢC TỐI ƯU SEO & FOR YOU PAGE:
   - Hashtag định danh ngách sản phẩm.
   - Hashtag xu hướng (Trending).
   - Hashtag chuyển đổi (Mua sắm, Review chân thực, Shopee Haul, TikTok Shop Haul).
"""

class ConversionComplianceAgent(BaseAgent):
    def __init__(self, model: Optional[str] = None):
        super().__init__(
            name="Compliance & Conversion Booster",
            role="Platform Policy & Conversion Rate Specialist",
            system_prompt=COMPLIANCE_SYSTEM_PROMPT,
            model=model,
        )

    def optimize_campaign(self, product_info: str, scripts_summary: str) -> str:
        prompt = f"""
Hãy kiểm duyệt và tối ưu chuyển đổi cho chiến dịch Affiliate của sản phẩm dưới đây:

THÔNG TIN SẢN PHẨM:
\"\"\"{product_info}\"\"\"

TÓM TẮT NỘI DUNG CHIẾN DỊCH:
\"\"\"{scripts_summary}\"\"\"

Hãy cung cấp:
1. Bảng rà soát các từ cấm/từ nhạy cảm cần tránh và từ thay thế.
2. Bộ CTA chốt đơn đỉnh cao (cho cả Giỏ hàng TikTok Shop và Link Bio/Comment Facebook).
3. Danh sách Hashtags chuẩn SEO đề xuất.
"""
        return self.think_and_act(prompt)
