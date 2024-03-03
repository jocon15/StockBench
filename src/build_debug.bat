:: Store the drc dir
set distPath=%cd%\dist\debug

pyinstaller main.py --name StockBench --onefile --noconfirm --distpath=dist\debug --icon=icon\candle.ico --version-file=version.YAML

:: remove any existing resources directory if it exists
del /f /s /q "%distPath%\icon"
rmdir /s /q "%distPath%\icon"

:: make a fresh resources dir in dist
mkdir "%distPath%\icon"

:: Copy specific resource sub dirs to the dist resource dir
xcopy "%cd%\icon\" "%distPath%\icon\*" /E /H /C /I /Y