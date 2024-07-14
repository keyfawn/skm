color 2
curl "https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe" --output python.exe
python.exe /passive InstallAllUsers=1 PrependPath=1 Include_test=0 SimpleInstall=1
DEL /F /A python.exe
cls
pip install -r requirements.txt
cls