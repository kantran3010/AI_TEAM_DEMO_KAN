import io
import os
import zipfile
from pathlib import Path
import streamlit as st

# Cấu hình giao diện Streamlit
st.set_page_config(
    page_title="AI Multi-Agent Team Hub",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

from ai_team.config import Config
from ai_team.affiliate.orchestrator import AffiliateOrchestrator
from ai_team.affiliate.agents.research_agent import AffiliateResearcherAgent
from ai_team.affiliate.agents.video_script_agent import VideoScriptAgent
from ai_team.affiliate.agents.social_copy_agent import SocialCopyAgent
from ai_team.affiliate.agents.visual_agent import VisualDesignerAgent
from ai_team.affiliate.agents.compliance_agent import ConversionComplianceAgent

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
        help="Khuyến nghị gemini-2.5-flash: Tốc độ cao, ngữ cảnh lớn và miễn phí.",
    )

    st.markdown("---")
    st.caption("🚀 AI Multi-Agent System | Local Workspace: `D:\\AI TEAM`")


# -------------------------------------------------------------
# TIÊU ĐỀ TRANG CHÍNH
# -------------------------------------------------------------
st.markdown(
    """
    <div style="text-align: center; margin-bottom: 25px;">
        <h1 style="color: #4A90E2; margin-bottom: 0;">🤖 AI MULTI-AGENT WORKSPACE</h1>
        <p style="font-size: 1.1rem; color: #888;">Nền Tảng Tự Động Hóa Đa Tác Tử: Lập Trình Phần Mềm & Affiliate Marketing Toàn Diện</p>
    </div>
    """,
    unsafe_allow_html=True,
)

tab_affiliate, tab_dev = st.tabs([
    "🛍️ TEAM BOT AFFILIATE MARKETING",
    "💻 TEAM AI LẬP TRÌNH PHẦN MỀM (DEV)",
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
        )

    with col_input:
        default_val = "" if preset == "Tự nhập..." else preset
        product_info = st.text_area(
            "📦 Nhập tên, đặc điểm nổi bật hoặc link sản phẩm Affiliate:",
            value=default_val,
            placeholder="Ví dụ: Bình giữ nhiệt inox 304 có màn hình LED báo nhiệt độ cảm ứng, giữ nóng/lạnh 12 tiếng, giá 99k trên TikTok Shop...",
            height=100,
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

            # Lưu vào session state để hiển thị
            st.session_state["affiliate_result"] = {
                "product": product_info,
                "research": research_res,
                "video": video_res,
                "social": social_res,
                "visual": visual_res,
                "compliance": compliance_res,
            }

    # Hiển thị kết quả nếu có trong session_state
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
            st.info("💡 Bạn chỉ việc copy câu Prompt tiếng Anh bên dưới dán vào Midjourney hoặc Bing Image Creator là có ngay bộ ảnh chuyên nghiệp!")
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
        )

    with col_dev_in:
        default_dev = "" if preset_dev == "Tự nhập..." else preset_dev
        dev_requirement = st.text_area(
            "📝 Nhập yêu cầu / phần mềm bạn muốn Team AI lập trình:",
            value=default_dev,
            placeholder="Ví dụ: Tạo ứng dụng quản lý chi tiêu cá nhân bằng Python CLI, cho phép thêm khoản thu/chi, tính tổng theo tháng và lưu file CSV...",
            height=100,
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

    # Hiển thị kết quả Dev Team
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

            # Nút tải file ZIP
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
