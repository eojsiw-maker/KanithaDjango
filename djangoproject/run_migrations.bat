@echo off
REM ใช้ python จาก venv เพื่อรันคำสั่ง Django
set PY=.venv\Scripts\python

if not exist "%PY%" (
    echo Virtualenv not found. Run setup_env.bat first.
    pause
    exit /b 1
)

echo Running makemigrations...
%PY% manage.py makemigrations

echo If conflicts appear, attempt merge:
%PY% manage.py makemigrations --merge || echo "No conflicts or merge not needed."

echo Applying migrations...
%PY% manage.py migrate

echo Seeding data (if seed_data command exists)...
%PY% manage.py seed_data || echo "seed_data not available or failed."

echo Done.
echo To create superuser: %PY% manage.py createsuperuser
pause
