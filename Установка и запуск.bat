@echo off
echo ============================================
echo   Установка калькулятора выездных работ
echo ============================================
echo.

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python не найден. Скачиваю Python...
    curl -o python_installer.exe https://www.python.org/ftp/python/3.12.5/python-3.12.5-amd64.exe
    python_installer.exe /quiet InstallAllUsers=1 PrependPath=1
    del python_installer.exe
    echo Перезагрузите компьютер и запустите этот файл снова.
    pause
    exit
)

echo Устанавливаю зависимости...
pip install streamlit python-docx reportlab

echo.
echo Готово! Запуск...
python -m streamlit run web.py
pause
