@echo off
REM สร้าง virtual environment ถ้ายังไม่มี
if not exist ".venv" (
    py -m venv .venv
)

REM อัพเดต pip และติดตั้ง dependencies ภายใน venv
.venv\Scripts\python -m pip install --upgrade pip
.venv\Scripts\python -m pip install -r requirements.txt

echo.
echo Virtualenv and dependencies installed.
echo To activate in this shell run: .venv\Scripts\activate
echo Or run commands via: .venv\Scripts\python manage.py <command>
pause
