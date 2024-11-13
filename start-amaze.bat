:: Mazeme bat entrypoint

@echo off
:: Change to the directory of this script (the .bat file location)
cd /d "%~dp0"

:: Run the Python script
python src/maze-game.py

:: Pause to display the script's output before closing
pause
