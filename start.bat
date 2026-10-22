@echo off
cd /d "%~dp0"
rem NASのUNCパスに書き換える
set STL_ROOT=\\NAS\stl
streamlit run app.py --server.address=0.0.0.0 --server.port=8501 --server.headless=true
