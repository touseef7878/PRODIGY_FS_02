@echo off
echo 🚀 Starting Employee Management System Backend...
cd backend
call venv\Scripts\activate.bat
echo ✅ Virtual environment activated
echo 🔄 Starting Flask server...
python wsgi.py