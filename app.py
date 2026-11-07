import io
import os
import json
import base64
import zipfile
from pathlib import Path
from typing import List, Dict, Any, Optional

import streamlit as st
import pandas as pd
from pypdf import PdfReader

# Cấu hình giao diện Streamlit
st.set_page_config(
    page_title="AI Multi-Agent Workspace | Nền Tảng AI Đa Năng",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

from ai_team.config import Config
from ai_team.llm import LLMClient
from ai_team.custom_agents import CustomAgentManager

# Affiliate Agents
from ai_team.affiliate.agents.research_agent import AffiliateResearcherAgent
from ai_team.affiliate.agents.video_script_agent import VideoScriptAgent
from ai_team.affiliate.agents.social_copy_agent import SocialCopyAgent
from ai_team.affiliate.agents.visual_agent import VisualDesignerAgent
from ai_team.affiliate.agents.compliance_agent import ConversionComplianceAgent

# Dev Agents
from ai_team.agents.scenario_agent import ScenarioAgent
from ai_team.agents.coder_agent import CoderAgent
from ai_team.agents.tester_agent import TesterAgent
from ai_team.utils.file_extractor import FileExtractor

# -------------------------------------------------------------
# SIDEBAR: CẤU HÌNH & API KEYS
# -------------------------------------------------------------
with st.sidebar:
    st.title("⚙️ Cấu Hình Hệ Thống")
    
    st.markdown("### 🔑 API Keys")
    gemini_key = st.text_input(
        "Google Gemini API Key",
        value=Config.GEMINI_API_KEY,
        type="password",
        help="Lấy miễn phí tại aistudio.google.com/app/apikey",
    )
    if gemini_key:
        os.environ["GEMINI_API_KEY"] = gemini_key
        Config.GEMINI_API_KEY = gemini_key

    openai_key = st.text_input(
        "OpenAI API Key (Tùy chọn)",
        value=Config.OPENAI_API_KEY,
        type="password",
    )
    if openai_key:
        os.environ["OPENAI_API_KEY"] = openai_key
        Config.OPENAI_API_KEY = openai_key

    groq_key = st.text_input(
        "Groq API Key (Tùy chọn)",
        value=Config.GROQ_API_KEY,
        type="password",
    )
    if groq_key:
        os.environ["GROQ_API_KEY"] = groq_key
        Config.GROQ_API_KEY = groq_key

    st.markdown("---")
    st.markdown("### 🧠 Mô Hình AI")
    model_choice = st.selectbox(
        "Chọn Model",
        options=[
            "gemini/gemini-2.5-flash",
            "gemini/gemini-1.5-pro",
            "openai/gpt-4o-mini",
            "openai/gpt-4o",
            "groq/llama-3.3-70b-versatile",
        ],
        index=0,
        help="Khuyến nghị gemini-2.5-flash: Tốc độ cao, đa năng, xử lý hình ảnh & văn bản lớn.",
    )

    st.markdown("---")
    st.caption("🚀 AI Multi-Agent OS | Workspace: `D:\\AI TEAM`")

# Helper function calling LLM
def ask_llm(prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.3) -> str:
    client = LLMClient(model=model_choice, temperature=temperature)
    return client.generate([{"role": "user", "content": prompt}], system_prompt=system_prompt)

# Helper function calling LLM with Image (Multimodal)
def ask_llm_vision(prompt: str, image_bytes: bytes, mime_type: str = "image/jpeg") -> str:
    client = LLMClient(model=model_choice, temperature=0.2)
    b64_image = base64.b64encode(image_bytes).decode("utf-8")
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{b64_image}"}},
            ],
        }
    ]
    return client.generate(messages)

# -------------------------------------------------------------
# TIÊU ĐỀ TRANG CHÍNH
# -------------------------------------------------------------
st.markdown(
    """
    <div style="text-align: center; margin-bottom: 25px;">
        <h1 style="color: #4A90E2; margin-bottom: 0;">🤖 ALL-IN-ONE AI MULTI-AGENT PLATFORM</h1>
        <p style="font-size: 1.15rem; color: #888;">Nền Tảng AI Đa Năng: Lập Trình, Affiliate Marketing, Phân Tích Dữ Liệu, Viết Lách, Custom Bots & Nghiên Cứu Sâu</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# 6 TABS CHÍNH
tab_affiliate, tab_dev, tab_analyst, tab_content, tab_bots, tab_chat = st.tabs([
    "🛍️ Team Affiliate",
    "💻 Team Lập Trình",
    "📊 Phân Tích Dữ Liệu & File",
    "✍️ Xưởng Viết Lách & Dịch",
    "🤖 Tự Tạo Bot Riêng",
    "💬 Trợ Lý Nghiên Cứu Sâu",
])


# =============================================================
# TAB 1: TEAM BOT AI AFFILIATE MARKETING
# =============================================================
with tab_affiliate:
    st.subheader("🛍️ Tự Động Hóa Chiến Dịch Affiliate Marketing Đa Kênh")
    st.info("💡 **Dây chuyền gồm 5 Bot:** 1. Nghiên cứu Insight & USP ➜ 2. Kịch bản Video TikTok ➜ 3. Bài viết Threads/FB ➜ 4. Mô tả tạo ảnh AI (Midjourney/Flux) ➜ 5. Rà soát từ cấm & CTA")

    col_input, col_preset = st.columns([3, 1])
    with col_preset:
        st.markdown("**Gợi ý mẫu:**")
        preset = st.selectbox(
            "Chọn sản phẩm mẫu",
            [
                "Tự nhập...",
                "Bình giữ nhiệt hiển thị nhiệt độ thông minh giá 99k Shopee",
                "Nồi chiên không dầu mini 3L Lock&Lock sale 50%",
                "Bàn phím cơ không dây Bluetooth Aula F75 cho dân văn phòng",
            ],
            index=0,
            key="affiliate_preset",
        )

    with col_input:
        default_val = "" if preset == "Tự nhập..." else preset
        product_info = st.text_area(
            "📦 Nhập tên, đặc điểm nổi bật hoặc link sản phẩm Affiliate:",
            value=default_val,
            placeholder="Ví dụ: Bình giữ nhiệt inox 304 có màn hình LED báo nhiệt độ cảm ứng, giữ nóng/lạnh 12 tiếng, giá 99k trên TikTok Shop...",
            height=100,
            key="affiliate_input",
        )

    btn_run_affiliate = st.button("🚀 BẮT ĐẦU CHẠY TEAM BOT AFFILIATE", type="primary", use_container_width=True)

    if btn_run_affiliate:
        if not product_info.strip():
            st.error("Vui lòng nhập thông tin sản phẩm!")
        elif not Config.validate_keys():
            st.error("Chưa có API Key! Vui lòng nhập Gemini hoặc OpenAI API Key ở thanh bên trái (Sidebar).")
        else:
            with st.status("🚀 Team Bot Affiliate đang làm việc...", expanded=True) as status:
                st.write("🕵️ **Bot 1:** Đang đào sâu Insight khách hàng và lập 5 góc tiếp cận triệu view...")
                research_agent = AffiliateResearcherAgent(model=model_choice)
                research_res = research_agent.analyze_product(product_info)
                st.write("✅ Bot 1 đã hoàn thành nghiên cứu sản phẩm!")

                st.write("🎬 **Bot 2:** Đang sáng tác 3 kịch bản video ngắn TikTok/Reels từng giây...")
                video_agent = VideoScriptAgent(model=model_choice)
                video_res = video_agent.write_scripts(research_res)
                st.write("✅ Bot 2 đã hoàn thành 3 kịch bản video ngắn!")

                st.write("✍️ **Bot 3:** Đang viết chuỗi bài Threads Viral, Facebook Group và Blog SEO...")
                social_agent = SocialCopyAgent(model=model_choice)
                social_res = social_agent.write_copy(research_res)
                st.write("✅ Bot 3 đã hoàn thành nội dung chữ đa kênh!")

                st.write("🎨 **Bot 4:** Đang thiết kế 5 concept hình ảnh giới thiệu & Prompts AI (Midjourney/Flux)...")
                visual_agent = VisualDesignerAgent(model=model_choice)
                visual_res = visual_agent.generate_image_prompts(product_info, research_res)
                st.write("✅ Bot 4 đã hoàn thành bộ mô tả hình ảnh & Prompts AI!")

                st.write("🛡️ **Bot 5:** Đang rà soát từ cấm sàn, tạo bộ CTA kích thích đơn hàng và Hashtags...")
                compliance_agent = ConversionComplianceAgent(model=model_choice)
                compliance_res = compliance_agent.optimize_campaign(
                    product_info, f"{research_res[:1000]}\n...\n{video_res[:1000]}"
                )
                st.write("✅ Bot 5 đã hoàn tất tối ưu chuyển đổi & kiểm duyệt!")

                status.update(label="🎉 Hoàn tất toàn bộ chiến dịch Affiliate!", state="complete", expanded=False)

            st.session_state["affiliate_result"] = {
                "product": product_info,
                "research": research_res,
                "video": video_res,
                "social": social_res,
                "visual": visual_res,
                "compliance": compliance_res,
            }

    if "affiliate_result" in st.session_state:
        res = st.session_state["affiliate_result"]
        st.success(f"📦 Chiến Dịch Cho Sản Phẩm: **{res['product']}**")

        subtab_all, subtab_visual, subtab_video, subtab_social, subtab_research, subtab_comp = st.tabs([
            "📋 Tất Cả Trong 1 (All-in-One)",
            "🎨 Mô Tả Tạo Ảnh AI (MỚI 🔥)",
            "🎬 Kịch Bản Video TikTok/Reels",
            "✍️ Threads & Facebook Group",
            "🕵️ Insight & 5 Góc Tiếp Cận",
            "🛡️ Rà Soát Từ Cấm & CTA",
        ])

        with subtab_all:
            st.markdown("### 🚀 File Tổng Hợp Toàn Bộ Chiến Dịch")
            all_content = f"# Chiến Dịch Affiliate: {res['product']}\n\n## 1. Nghiên Cứu\n{res['research']}\n\n## 2. Kịch Bản Video\n{res['video']}\n\n## 3. Nội Dung Chữ Đa Kênh\n{res['social']}\n\n## 4. Mô Tả Tạo Ảnh AI\n{res['visual']}\n\n## 5. Từ Cấm & CTA\n{res['compliance']}"
            st.download_button(
                "📥 Tải Về Toàn Bộ Chiến Dịch (.md)",
                data=all_content,
                file_name="affiliate_campaign.md",
                mime="text/markdown",
            )
            st.markdown(all_content)

        with subtab_visual:
            st.markdown("### 🎨 Bộ Ý Tưởng Hình Ảnh Giới Thiệu & Prompts AI (Midjourney / Flux / DALL-E)")
            st.info("💡 Copy câu Prompt tiếng Anh bên dưới dán vào Midjourney hoặc Bing Image Creator là có ngay bộ ảnh chuyên nghiệp!")
            st.markdown(res["visual"])

        with subtab_video:
            st.markdown("### 🎬 3 Kịch Bản Video Ngắn Phân Cảnh Từng Giây")
            st.markdown(res["video"])

        with subtab_social:
            st.markdown("### ✍️ Bài Đăng Threads Viral, Review Facebook Group & Blog SEO")
            st.markdown(res["social"])

        with subtab_research:
            st.markdown("### 🕵️ Phân Tích Chân Dung Khách Hàng & 5 Góc Tiếp Cận Triệu View")
            st.markdown(res["research"])

        with subtab_comp:
            st.markdown("### 🛡️ Danh Sách Từ Cấm Cần Tránh & Bộ Lời Kêu Gọi Hành Động (CTA)")
            st.markdown(res["compliance"])


# =============================================================
# TAB 2: TEAM AI LẬP TRÌNH PHẦN MỀM (DEV TEAM)
# =============================================================
with tab_dev:
    st.subheader("💻 Team AI Lập Trình & Kiểm Thử Tự Động (Self-Healing)")
    st.info("💡 **Dây chuyền gồm 3 Agent:** 1. Kịch bản đặc tả (SRS) ➜ 2. Viết toàn bộ mã nguồn Python ➜ 3. Viết Pytest, chạy test thực tế & tự vá lỗi nếu có bug")

    col_dev_in, col_dev_preset = st.columns([3, 1])
    with col_dev_preset:
        st.markdown("**Gợi ý phần mềm:**")
        preset_dev = st.selectbox(
            "Chọn ý tưởng mẫu",
            [
                "Tự nhập...",
                "Ứng dụng Todo List CLI có lưu file JSON và phân loại việc ưu tiên",
                "Tool tính chỉ số BMI và gợi ý thực đơn calo hàng ngày bằng Python",
                "Bộ chuyển đổi tiền tệ tự động có cache tỷ giá và giao diện dòng lệnh",
            ],
            index=0,
            key="dev_preset",
        )

    with col_dev_in:
        default_dev = "" if preset_dev == "Tự nhập..." else preset_dev
        dev_requirement = st.text_area(
            "📝 Nhập yêu cầu / phần mềm bạn muốn Team AI lập trình:",
            value=default_dev,
            placeholder="Ví dụ: Tạo ứng dụng quản lý chi tiêu cá nhân bằng Python CLI, cho phép thêm khoản thu/chi, tính tổng theo tháng và lưu file CSV...",
            height=100,
            key="dev_input",
        )

    btn_run_dev = st.button("💻 BẮT ĐẦU LẬP TRÌNH & KIỂM THỬ", type="primary", use_container_width=True)

    if btn_run_dev:
        if not dev_requirement.strip():
            st.error("Vui lòng nhập yêu cầu phần mềm!")
        elif not Config.validate_keys():
            st.error("Chưa có API Key! Vui lòng nhập Gemini hoặc OpenAI API Key ở thanh bên trái (Sidebar).")
        else:
            workspace_dir = Path("workspace").resolve()
            project_dir = workspace_dir / "project"
            project_dir.mkdir(parents=True, exist_ok=True)

            with st.status("💻 Team Dev đang thực hiện dự án...", expanded=True) as status_dev:
                st.write("📝 **Agent 1 (Spec Writer):** Đang phân tích yêu cầu và viết kịch bản đặc tả...")
                scenario_agent = ScenarioAgent(model=model_choice)
                spec_content = scenario_agent.write_spec(dev_requirement)
                st.write("✅ Đã hoàn thành kịch bản đặc tả kỹ thuật!")

                st.write("💻 **Agent 2 (Coder):** Đang lập trình toàn bộ các file mã nguồn...")
                coder_agent = CoderAgent(model=model_choice)
                raw_code = coder_agent.generate_code(spec_content)
                code_files = FileExtractor.extract_files(raw_code)
                if not code_files:
                    code_files = {"main.py": raw_code}
                FileExtractor.save_files(code_files, project_dir)
                st.write(f"✅ Đã tạo {len(code_files)} file mã nguồn vào `workspace/project/`!")

                st.write("🧪 **Agent 3 (QA Tester):** Đang viết bộ kiểm thử tự động với Pytest...")
                tester_agent = TesterAgent(model=model_choice)
                raw_tests = tester_agent.generate_tests(spec_content, code_files)
                test_files = FileExtractor.extract_files(raw_tests)
                if not test_files:
                    test_files = {"tests/test_main.py": raw_tests}
                FileExtractor.save_files(test_files, project_dir)
                st.write(f"✅ Đã tạo {len(test_files)} file kiểm thử vào `workspace/project/tests/`!")

                st.write("⚙️ **QA & CI Runner:** Đang chạy Pytest thực tế và kiểm tra chất lượng...")
                is_passed, total, passed_cnt, failed_cnt, test_output = tester_agent.run_tests(project_dir)

                round_idx = 0
                max_retries = 3
                while not is_passed and round_idx < max_retries:
                    round_idx += 1
                    st.write(f"🔄 **Tự sửa lỗi (Lần {round_idx}):** Coder đang phân tích lỗi và sửa mã nguồn...")
                    current_src = {p.relative_to(project_dir).as_posix(): p.read_text(encoding="utf-8") for p in project_dir.rglob("*.py") if "tests" not in p.parts}
                    fixed_raw = coder_agent.fix_code(spec_content, current_src, test_output)
                    fixed_files = FileExtractor.extract_files(fixed_raw)
                    if fixed_files:
                        FileExtractor.save_files(fixed_files, project_dir)
                    is_passed, total, passed_cnt, failed_cnt, test_output = tester_agent.run_tests(project_dir)

                if is_passed:
                    status_dev.update(label="🎉 Tuyệt vời! Toàn bộ kiểm thử đã vượt qua (100% PASS)!", state="complete", expanded=False)
                else:
                    status_dev.update(label="⚠ Đã hoàn thành một phần (Cần kiểm tra thêm)", state="error", expanded=False)

            st.session_state["dev_result"] = {
                "requirement": dev_requirement,
                "spec": spec_content,
                "code_files": {p.relative_to(project_dir).as_posix(): p.read_text(encoding="utf-8") for p in project_dir.rglob("*.py")},
                "is_passed": is_passed,
                "test_output": test_output,
                "total": total,
                "passed_cnt": passed_cnt,
                "failed_cnt": failed_cnt,
            }

    if "dev_result" in st.session_state:
        dres = st.session_state["dev_result"]
        if dres["is_passed"]:
            st.success(f"✔ Đã lập trình và kiểm thử thành công: **{dres['passed_cnt']}/{dres['total']} bài test PASS (100%)**!")
        else:
            st.warning(f"⚠ Kết quả test: {dres['passed_cnt']}/{dres['total']} PASS. Xem chi tiết bên dưới.")

        dev_tab_code, dev_tab_spec, dev_tab_test = st.tabs([
            "💻 Mã Nguồn Dự Án (Source Code)",
            "📋 Kịch Bản & Đặc Tả (SRS)",
            "🧪 Báo Cáo Kiểm Thử (Pytest)",
        ])

        with dev_tab_code:
            st.markdown("### 📁 Các file mã nguồn đã tạo:")
            for fname, fcontent in dres["code_files"].items():
                with st.expander(f"📄 {fname}", expanded=True):
                    st.code(fcontent, language="python")

            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                for fname, fcontent in dres["code_files"].items():
                    zip_file.writestr(fname, fcontent)
            zip_buffer.seek(0)

            st.download_button(
                "📥 Tải Toàn Bộ Code Dự Án (.zip)",
                data=zip_buffer,
                file_name="ai_dev_project.zip",
                mime="application/zip",
            )

        with dev_tab_spec:
            st.markdown("### 📋 Kịch Bản Đặc Tả Kỹ Thuật (SRS)")
            st.markdown(dres["spec"])

        with dev_tab_test:
            st.markdown("### 🧪 Chi Tiết Kết Quả Chạy Pytest")
            st.code(dres["test_output"], language="bash")


# =============================================================
# TAB 3: PHÂN TÍCH FILE & DỮ LIỆU (DATA & DOC ANALYST)
# =============================================================
with tab_analyst:
    st.subheader("📊 Trợ Lý Phân Tích Tài Liệu & Dữ Liệu Thông Minh")
    st.info("💡 Hỗ trợ: **Excel (.xlsx), CSV, PDF, TXT, JSON, và Hình ảnh (.png, .jpg)** để tóm tắt văn bản, phân tích số liệu kinh doanh hoặc thị giác máy tính!")

    uploaded_file = st.file_uploader(
        "📂 Kéo thả hoặc chọn file để phân tích:",
        type=["pdf", "xlsx", "xls", "csv", "txt", "json", "png", "jpg", "jpeg"],
        key="analyst_file_uploader",
    )

    if uploaded_file is not None:
        file_name = uploaded_file.name
        file_ext = file_name.split(".")[-1].lower()

        # 1. XỬ LÝ FILE CSV / EXCEL
        if file_ext in ["csv", "xlsx", "xls"]:
            try:
                if file_ext == "csv":
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)

                st.success(f"📊 Đã tải dữ liệu thành công: **{file_name}** ({df.shape[0]} dòng, {df.shape[1]} cột)")

                col_view, col_stat = st.columns([2, 1])
                with col_view:
                    st.markdown("**Bảng Dữ Liệu Xem Trước (Top 50 dòng):**")
                    st.dataframe(df.head(50), use_container_width=True)

                with col_stat:
                    st.markdown("**Thống Kê Mô Tả Nhanh:**")
                    st.dataframe(df.describe(), use_container_width=True)

                # Vẽ biểu đồ tương tác nhanh
                numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
                if numeric_cols:
                    st.markdown("#### 📈 Vẽ Biểu Đồ Nhanh")
                    c_chart1, c_chart2, c_chart3 = st.columns(3)
                    with c_chart1:
                        chart_type = st.selectbox("Loại biểu đồ", ["Cột (Bar)", "Đường (Line)", "Vùng (Area)"])
                    with c_chart2:
                        x_col = st.selectbox("Trục X (Nhãn)", df.columns.tolist())
                    with c_chart3:
                        y_col = st.selectbox("Trục Y (Số liệu)", numeric_cols)

                    chart_data = df[[x_col, y_col]].set_index(x_col)
                    if chart_type == "Cột (Bar)":
                        st.bar_chart(chart_data)
                    elif chart_type == "Đường (Line)":
                        st.line_chart(chart_data)
                    else:
                        st.area_chart(chart_data)

                # Hỏi đáp dữ liệu với AI
                st.markdown("#### 🤖 Hỏi AI Về Bảng Dữ Liệu Này")
                data_query = st.text_input(
                    "Nhập câu hỏi của bạn:",
                    placeholder="Ví dụ: Phân tích 3 xu hướng quan trọng nhất, các điểm bất thường và đề xuất giải pháp tối ưu doanh thu...",
                    key="csv_query",
                )
                if st.button("🔍 Phân Tích Bằng AI", key="btn_csv_ai"):
                    with st.spinner("AI đang tính toán và phân tích bảng số liệu..."):
                        data_summary = f"Tên file: {file_name}\nSố dòng: {df.shape[0]}, Số cột: {df.shape[1]}\nCác cột: {list(df.columns)}\nTop 10 dòng:\n{df.head(10).to_string()}\nThống kê mô tả:\n{df.describe().to_string()}"
                        system_prompt = "Bạn là một Chuyên gia Phân Tích Dữ Liệu Kinh Doanh (Senior Data & BI Analyst). Hãy trả lời câu hỏi dựa trên dữ liệu được cung cấp, nêu rõ các con số, xu hướng và đề xuất thực thi sắc bén."
                        analysis = ask_llm(f"Dữ liệu bảng:\n{data_summary}\n\nCâu hỏi: {data_query}", system_prompt=system_prompt)
                        st.markdown(analysis)

            except Exception as e:
                st.error(f"Lỗi khi đọc file bảng tính: {str(e)}")

        # 2. XỬ LÝ FILE PDF / VĂN BẢN
        elif file_ext in ["pdf", "txt", "json"]:
            try:
                extracted_text = ""
                if file_ext == "pdf":
                    pdf_reader = PdfReader(uploaded_file)
                    for page in pdf_reader.pages:
                        extracted_text += page.extract_text() or ""
                else:
                    extracted_text = uploaded_file.read().decode("utf-8", errors="ignore")

                word_count = len(extracted_text.split())
                st.success(f"📄 Đã đọc văn bản: **{file_name}** ({word_count:,} từ)")

                with st.expander("👁️ Xem trích đoạn văn bản (1,000 ký tự đầu)", expanded=False):
                    st.text(extracted_text[:1000] + ("..." if len(extracted_text) > 1000 else ""))

                col_b1, col_b2 = st.columns(2)
                with col_b1:
                    btn_sum = st.button("📝 Tóm Tắt Ý Chính & Điểm Mấu Chốt", use_container_width=True)
                with col_b2:
                    btn_qa = st.button("🔍 Đánh Giá Rủi Ro & Cơ Hội", use_container_width=True)

                if btn_sum:
                    with st.spinner("AI đang đọc hiểu và tóm tắt văn bản..."):
                        prompt = f"VĂN BẢN TÀI LIỆU:\n\"\"\"{extracted_text[:30000]}\"\"\"\n\nHãy tóm tắt văn bản trên thành bản Executive Summary chuyên nghiệp gồm: 1. Mục tiêu cốt lõi; 2. Các ý chính quan trọng nhất; 3. Hành động đề xuất."
                        st.markdown(ask_llm(prompt))

                if btn_qa:
                    with st.spinner("AI đang phân tích rủi ro và cơ hội..."):
                        prompt = f"VĂN BẢN TÀI LIỆU:\n\"\"\"{extracted_text[:30000]}\"\"\"\n\nHãy phân tích sâu: 1. Các rủi ro tiềm ẩn hoặc điểm bất lợi; 2. Các cơ hội và lợi thế cạnh tranh; 3. Khuyến nghị chiến lược."
                        st.markdown(ask_llm(prompt))

                doc_user_q = st.text_input("❓ Đặt câu hỏi cụ thể về tài liệu này:", key="doc_user_q")
                if st.button("Hỏi AI Về Tài Liệu", key="btn_doc_q"):
                    if doc_user_q.strip():
                        with st.spinner("AI đang tra cứu câu trả lời trong tài liệu..."):
                            prompt = f"TÀI LIỆU NGUỒN:\n\"\"\"{extracted_text[:30000]}\"\"\"\n\nCÂU HỎI:\n{doc_user_q}\n\nHãy trả lời chính xác dựa trên tài liệu trên, trích dẫn nội dung minh chứng nếu có."
                            st.markdown(ask_llm(prompt))

            except Exception as e:
                st.error(f"Lỗi khi đọc tài liệu văn bản: {str(e)}")

        # 3. XỬ LÝ FILE HÌNH ẢNH (VISION AI)
        elif file_ext in ["png", "jpg", "jpeg"]:
            try:
                img_bytes = uploaded_file.read()
                col_img, col_act = st.columns([1, 1])
                with col_img:
                    st.image(img_bytes, caption=f"Ảnh: {file_name}", use_container_width=True)

                with col_act:
                    st.markdown("#### 👁️ Hỏi AI Về Hình Ảnh Này")
                    vision_preset = st.selectbox(
                        "Chọn tác vụ nhanh:",
                        [
                            "Tự nhập câu hỏi...",
                            "Đọc và trích xuất toàn bộ chữ trong ảnh (OCR)",
                            "Phân tích hóa đơn, phiếu thu, bảng số liệu trong ảnh",
                            "Mô tả chi tiết nội dung, màu sắc và góc chụp nghệ thuật của ảnh",
                        ],
                    )

                    default_vq = "" if vision_preset == "Tự nhập câu hỏi..." else vision_preset
                    vision_query = st.text_area("Câu hỏi / Yêu cầu của bạn:", value=default_vq, height=80)
                    btn_vision = st.button("🔍 Phân Tích Ảnh Bằng Vision AI", type="primary")

                if btn_vision:
                    if not vision_query.strip():
                        st.error("Vui lòng nhập câu hỏi về hình ảnh!")
                    else:
                        with st.spinner("AI Vision đang quan sát và phân tích hình ảnh..."):
                            mime = "image/png" if file_ext == "png" else "image/jpeg"
                            v_ans = ask_llm_vision(vision_query, img_bytes, mime_type=mime)
                            st.markdown("### 📋 Kết Quả Phân Tích Hình Ảnh:")
                            st.markdown(v_ans)

            except Exception as e:
                st.error(f"Lỗi khi xử lý hình ảnh: {str(e)}")


# =============================================================
# TAB 4: XƯỞNG VIẾT LÁCH & DỊCH THUẬT (CONTENT STUDIO)
# =============================================================
with tab_content:
    st.subheader("✍️ Xưởng Sáng Tạo Nội Dung & Dịch Thuật Đa Năng")
    st.info("💡 Soạn thảo nhanh **Email công việc, Dàn ý Slide thuyết trình, Bài PR báo chí, SEO Blog và Dịch thuật ngữ cảnh sâu**.")

    content_mode = st.radio(
        "Chọn loại nội dung muốn tạo:",
        ["📧 Email Công Việc", "📑 Dàn Ý Slide Thuyết Trình", "📰 Bài Báo & SEO Blog", "🌐 Dịch Thuật Chuyên Sâu"],
        horizontal=True,
    )

    # 1. EMAIL
    if content_mode == "📧 Email Công Việc":
        col_e1, col_e2 = st.columns(2)
        with col_e1:
            email_purpose = st.selectbox(
                "Mục đích Email:",
                ["Thương lượng giá / Đối tác", "Ứng tuyển / Thư xin việc (Cover Letter)", "Từ chối lịch sự đối tác/lời mời", "Đòi công nợ / Nhắc thanh toán khéo léo", "Báo cáo tiến độ cho Sếp", "Thư cảm ơn sau cuộc họp"],
            )
            email_tone = st.selectbox("Giọng văn:", ["Chuyên nghiệp & Lịch sự", "Trang trọng & Cứng rắn", "Thân thiện & Cởi mở", "Ngắn gọn súc tích"])
        with col_e2:
            email_points = st.text_area(
                "Các ý chính cần có trong email:",
                placeholder="Ví dụ: Đã nhận được báo giá ngày 5/11, muốn xin chiết khấu 15% vì đơn hàng số lượng lớn, hẹn phản hồi trước thứ 6...",
                height=120,
            )

        if st.button("✉️ Soạn Email Tự Động", type="primary"):
            if not email_points.strip():
                st.error("Vui lòng nhập ý chính của email!")
            else:
                with st.spinner("AI đang soạn thảo 2 phiên bản email..."):
                    prompt = f"Hãy viết email công việc chuyên nghiệp bằng Tiếng Việt:\n- Mục đích: {email_purpose}\n- Giọng văn: {email_tone}\n- Các ý chính: {email_points}\n\nHãy xuất ra 2 phiên bản: Phiên bản 1 (Ngắn gọn súc tích) và Phiên bản 2 (Đầy đủ, chi tiết, trang trọng)."
                    st.markdown(ask_llm(prompt, temperature=0.4))

    # 2. SLIDE THUYẾT TRÌNH
    elif content_mode == "📑 Dàn Ý Slide Thuyết Trình":
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            slide_topic = st.text_input("Chủ đề bài thuyết trình:", placeholder="Ví dụ: Chiến lược phát triển sản phẩm công nghệ AI năm 2026")
            slide_count = st.slider("Số lượng Slide:", min_value=5, max_value=20, value=8)
        with col_s2:
            slide_audience = st.selectbox("Đối tượng người nghe:", ["Nhà đầu tư / Ban Giám Đốc", "Khách hàng doanh nghiệp (B2B)", "Nhân viên nội bộ công ty", "Sinh viên / Đại chúng"])
            slide_style = st.selectbox("Phong cách trình bày:", ["Mô hình khởi nghiệp (Pitch Deck)", "Báo cáo kinh doanh (Executive)", "Truyền cảm hứng & Đào tạo"])

        if st.button("📑 Tạo Dàn Ý Slide Thuyết Trình", type="primary"):
            if not slide_topic.strip():
                st.error("Vui lòng nhập chủ đề slide!")
            else:
                with st.spinner("AI đang thiết kế cấu trúc slide từng trang..."):
                    prompt = f"Hãy thiết kế dàn ý chi tiết bài thuyết trình PowerPoint ({slide_count} slides) về chủ đề: \"{slide_topic}\".\n- Đối tượng nghe: {slide_audience}\n- Phong cách: {slide_style}\n\nMỗi slide cần có: 1. Tiêu đề slide; 2. Các gạch đầu dòng nội dung chính; 3. Gợi ý hình ảnh/icon minh họa; 4. Lời thoại gợi ý của người thuyết trình (Speaker Notes)."
                    st.markdown(ask_llm(prompt, temperature=0.5))

    # 3. BÀI BÁO & SEO BLOG
    elif content_mode == "📰 Bài Báo & SEO Blog":
        col_a1, col_a2 = st.columns(2)
        with col_a1:
            article_topic = st.text_input("Tiêu đề / Chủ đề bài viết:", placeholder="Ví dụ: Xu hướng Trí tuệ Nhân tạo đa tác tử và cơ hội nghề nghiệp 2026")
            target_keywords = st.text_input("Từ khóa SEO mục tiêu:", placeholder="Ví dụ: AI Multi-Agent, tự động hóa, xu hướng công nghệ")
        with col_a2:
            article_type = st.selectbox("Thể loại:", ["Bài viết Blog chuẩn SEO", "Thông cáo báo chí (PR Article)", "Bài phân tích chuyên sâu (Case Study)"])
            article_length = st.selectbox("Độ dài mong muốn:", ["Khoảng 800 - 1,200 từ", "Khoảng 1,500 - 2,500 từ chuyên sâu"])

        if st.button("📰 Viết Bài Chuẩn SEO", type="primary"):
            if not article_topic.strip():
                st.error("Vui lòng nhập chủ đề bài viết!")
            else:
                with st.spinner("AI đang biên tập bài viết chuyên nghiệp..."):
                    prompt = f"Hãy viết một {article_type} hoàn chỉnh về chủ đề: \"{article_topic}\".\n- Từ khóa SEO: {target_keywords}\n- Độ dài: {article_length}\n\nYêu cầu: Có tiêu đề H1 giật tít thu hút, mở đầu cuốn hút, các đề mục H2, H3 logic, chèn từ khóa tự nhiên, có số liệu/dẫn chứng minh họa và phần kết luận kêu gọi hành động."
                    st.markdown(ask_llm(prompt, temperature=0.6))

    # 4. DỊCH THUẬT
    else:
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            src_lang = st.selectbox("Ngôn ngữ nguồn:", ["Tiếng Việt", "Tiếng Anh", "Tiếng Trung", "Tiếng Nhật", "Tiếng Hàn", "Tiếng Pháp"])
        with col_t2:
            dst_lang = st.selectbox("Ngôn ngữ đích:", ["Tiếng Anh", "Tiếng Việt", "Tiếng Trung", "Tiếng Nhật", "Tiếng Hàn", "Tiếng Pháp"], index=0)

        trans_style = st.selectbox("Văn phong dịch:", ["Tự nhiên chuẩn bản xứ (Native Casual)", "Trang trọng trong kinh doanh (Business Professional)", "Kỹ thuật chuyên ngành chính xác (Technical)", "Văn học nghệ thuật (Literary)"])
        trans_text = st.text_area("Nhập văn bản cần dịch:", height=150)

        if st.button("🌐 Dịch Thuật Chuyên Sâu", type="primary"):
            if not trans_text.strip():
                st.error("Vui lòng nhập văn bản cần dịch!")
            else:
                with st.spinner("AI đang dịch thuật và phân tích ngữ cảnh..."):
                    prompt = f"Hãy dịch văn bản sau từ {src_lang} sang {dst_lang} theo văn phong \"{trans_style}\".\n\nVĂN BẢN GỐC:\n\"\"\"{trans_text}\"\"\"\n\nYêu cầu xuất ra:\n1. BẢN DỊCH CHUẨN XỊN (mượt mà, không dịch thô gượng gạo).\n2. GIẢI THÍCH NGỮ CẢNH & TỪ VỰNG HAY (nêu các collocations, thành ngữ đắt giá được sử dụng)."
                    st.markdown(ask_llm(prompt, temperature=0.2))


# =============================================================
# TAB 5: TỰ TẠO BOT RIÊNG (CUSTOM AGENT BUILDER)
# =============================================================
with tab_bots:
    st.subheader("🤖 Xưởng Tạo Bot AI Riêng Biệt (Custom Agent Builder)")
    st.info("💡 Bạn có thể **chọn trò chuyện với 6 Bot chuyên gia có sẵn** hoặc **tự tạo ra bất kỳ con Bot nào** chỉ trong 10 giây để giải quyết công việc đặc thù!")

    agents_list = CustomAgentManager.load_agents()

    col_bot_select, col_bot_create = st.columns([2, 1])

    # FORM TẠO BOT MỚI
    with col_bot_create:
        with st.expander("➕ TỰ TẠO BOT MỚI THEO Ý BẠN", expanded=False):
            new_bot_name = st.text_input("Tên Bot:", placeholder="Ví dụ: Thầy Giáo Dạy Tiếng Trung")
            new_bot_icon = st.text_input("Icon Emoji:", value="🤖", max_chars=2)
            new_bot_role = st.text_input("Vai trò ngắn gọn:", placeholder="Ví dụ: Giáo viên dạy khẩu ngữ HSK 5")
            new_bot_prompt = st.text_area(
                "Chỉ dẫn tính cách & nhiệm vụ (System Prompt):",
                placeholder="Ví dụ: Bạn là thầy giáo tiếng Trung nhiệt tình. Hãy sửa phát âm pinyin, giải thích chữ Hán và đàm thoại cùng học viên...",
                height=120,
            )
            new_bot_temp = st.slider("Độ sáng tạo:", 0.0, 1.0, 0.5, 0.1)

            if st.button("💾 Lưu Bot Mới Vào Hệ Thống", type="primary", use_container_width=True):
                if not new_bot_name.strip() or not new_bot_prompt.strip():
                    st.error("Vui lòng nhập tên và chỉ dẫn hệ thống của Bot!")
                else:
                    CustomAgentManager.add_agent(
                        name=new_bot_name,
                        icon=new_bot_icon,
                        role=new_bot_role,
                        system_prompt=new_bot_prompt,
                        temperature=new_bot_temp,
                    )
                    st.success(f"🎉 Đã tạo thành công Bot: {new_bot_icon} {new_bot_name}!")
                    st.rerun()

    # CHỌN VÀ CHAT VỚI BOT
    with col_bot_select:
        bot_names = [f"{b.get('icon', '🤖')} {b['name']} — {b.get('role', '')}" for b in agents_list]
        selected_idx = st.selectbox("Chọn Bot bạn muốn trò chuyện:", range(len(bot_names)), format_func=lambda i: bot_names[i])
        current_bot = agents_list[selected_idx]

        st.markdown(f"### {current_bot.get('icon', '🤖')} {current_bot['name']}")
        st.caption(f"**Vai trò:** {current_bot.get('role', '')}")

        with st.expander("📜 Xem System Prompt của Bot", expanded=False):
            st.text(current_bot["system_prompt"])

        # Chat interface với bot
        bot_id = current_bot["id"]
        chat_key = f"bot_chat_{bot_id}"
        if chat_key not in st.session_state:
            st.session_state[chat_key] = []

        # Hiển thị lịch sử chat của bot này
        for msg in st.session_state[chat_key]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        user_msg = st.chat_input(f"Hỏi {current_bot['name']}...", key=f"chat_input_{bot_id}")
        if user_msg:
            st.session_state[chat_key].append({"role": "user", "content": user_msg})
            with st.chat_message("user"):
                st.markdown(user_msg)

            with st.chat_message("assistant"):
                with st.spinner(f"{current_bot['name']} đang suy nghĩ..."):
                    # Construct message history
                    history = [{"role": m["role"], "content": m["content"]} for m in st.session_state[chat_key]]
                    client = LLMClient(model=model_choice, temperature=current_bot.get("temperature", 0.4))
                    bot_ans = client.generate(history, system_prompt=current_bot["system_prompt"])
                    st.markdown(bot_ans)
                    st.session_state[chat_key].append({"role": "assistant", "content": bot_ans})

        if st.session_state[chat_key]:
            if st.button("🗑️ Xóa Lịch Sử Đoạn Chat Này", key=f"clear_bot_{bot_id}"):
                st.session_state[chat_key] = []
                st.rerun()


# =============================================================
# TAB 6: TRỢ LÝ TRÒ CHUYỆN & NGHIÊN CỨU SÂU (DEEP RESEARCH CHAT)
# =============================================================
with tab_chat:
    st.subheader("💬 Trợ Lý AI Trò Chuyện & Nghiên Cứu Sâu (Deep Research)")
    st.info("💡 Trò chuyện tự do hoặc bật chế độ **Deep Research** để AI phân tích đa chiều, bẻ gãy vấn đề phức tạp thành từng bước logic.")

    col_c1, col_c2 = st.columns([3, 1])
    with col_c2:
        deep_mode = st.toggle("🧠 Bật Chế Độ Deep Research", value=True, help="Kích hoạt tư duy phản biện đa chiều và phân tích từng bước chi tiết.")
        if st.button("🗑️ Xóa Cuộc Trò Chuyện", use_container_width=True):
            st.session_state["main_chat_history"] = []
            st.rerun()

    if "main_chat_history" not in st.session_state:
        st.session_state["main_chat_history"] = []

    # Hiển thị lịch sử chat
    for m in st.session_state["main_chat_history"]:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    main_user_input = st.chat_input("Nhập câu hỏi hoặc chủ đề bạn muốn nghiên cứu sâu...", key="main_chat_input")
    if main_user_input:
        st.session_state["main_chat_history"].append({"role": "user", "content": main_user_input})
        with st.chat_message("user"):
            st.markdown(main_user_input)

        with st.chat_message("assistant"):
            with st.spinner("AI đang tư duy và nghiên cứu sâu..."):
                sys_prompt = "Bạn là một Nhà Khoa Học & Cố Vấn Nghiên Cứu Toàn Năng (Chief Research Scientist). Trả lời thông tuệ, lập luận chặt chẽ, khách quan và đưa ra giải pháp toàn diện."
                if deep_mode:
                    sys_prompt += "\n\nHÃY ÁP DỤNG QUY TRÌNH DEEP RESEARCH:\n1. Phân tích bản chất câu hỏi và các giả định ngầm.\n2. Lập luận đa góc nhìn (Ưu điểm, Nhược điểm, Bất ngờ, Trường hợp biên).\n3. Đưa ra lộ trình hành động hoặc câu trả lời có tính ứng dụng cao nhất."

                history = [{"role": msg["role"], "content": msg["content"]} for msg in st.session_state["main_chat_history"]]
                client = LLMClient(model=model_choice, temperature=0.3)
                ans = client.generate(history, system_prompt=sys_prompt)
                st.markdown(ans)
                st.session_state["main_chat_history"].append({"role": "assistant", "content": ans})

        # Nút xuất lịch sử chat
        chat_export = "\n\n---\n\n".join([f"**{m['role'].upper()}:**\n{m['content']}" for m in st.session_state["main_chat_history"]])
        st.download_button("📥 Xuất Cuộc Trò Chuyện (.md)", data=chat_export, file_name="deep_research_chat.md", mime="text/markdown")
