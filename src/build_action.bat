pyinstaller src\main.py --name StockBench --onefile --windowed --noconfirm --distpath=src\dist\release --icon=src\resources\images\candle.ico --version-file=src\version.YAML

:: remove any existing resources directory if it exists
del /f /s /q "src\dist\resources"
rmdir /s /q "src\dist\resources"

:: make a fresh resources dir in dist
mkdir "src\dist\resources"

:: Copy specific resource sub dirs to the dist resource dir
xcopy "src\dist\resources\" "src\dist\resources\*" /E /H /C /I /Y
