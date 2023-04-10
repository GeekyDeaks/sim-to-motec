pyinstaller --onefile ams2.py
pyinstaller --add-data stm\gt7\db\*.csv;stm\gt7\db --onefile gt7.py 