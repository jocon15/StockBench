:: Store the drc dir
set distPath=%cd%\dist\release

pyinstaller main.py --name StockBench --onefile --windowed --noconfirm --distpath=dist\release --icon=icon\candle.ico --version-file=version.YAML

:: remove any existing resources directory if it exists
del /f /s /q "%distPath%\icon"
rmdir /s /q "%distPath%\icon"

:: make a fresh resources dir in dist
mkdir "%distPath%\icon"

:: Copy specific resource sub dirs to the dist resource dir
xcopy "%cd%\icon\" "%distPath%\icon\*" /E /H /C /I /Y