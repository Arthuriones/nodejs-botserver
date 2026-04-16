@echo off
echo === Combo Companion - Build ===
echo.

pip install -r requirements.txt
pip install pyinstaller

echo.
echo Compilando .exe...
echo.

pyinstaller --onefile --noconsole --name "ComboCompanion" main.py

echo.
echo === Build concluido! ===
echo O .exe esta em: dist\ComboCompanion.exe
echo.
pause
