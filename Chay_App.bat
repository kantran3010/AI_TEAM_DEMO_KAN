@echo off
chcp 65001 > nul
title AI Multi-Agent Team Hub
cd /d "%~dp0"
echo ========================================================
echo   🤖 ĐANG KHỞI ĐỘNG AI MULTI-AGENT WORKSPACE...
echo   💻 Team Dev: Lập Trình & Kiểm Thử Tự Động
echo   🛍️ Team Affiliate: Video TikTok + Bài Viết + Ảnh AI
echo ========================================================
echo.
echo Ứng dụng sẽ tự động mở trên trình duyệt web của bạn...
echo.
uv run streamlit run app.py
pause
