:: Store the drc dir
set distPath=%cd%\dist\debug

pyinstaller main.py --name StockBench --onefile --noconfirm --distpath=dist\debug --icon=resources\images\candle.ico --version-file=version.YAML

:: remove any existing resources directory if it exists
del /f /s /q "%distPath%\resources"
rmdir /s /q "%distPath%\resources"

:: make a fresh resources dir in dist
mkdir "%distPath%\resources"

:: Copy specific resource sub dirs to the dist resource dir
xcopy "%cd%\resources\" "%distPath%\resources\*" /E /H /C /I /Y