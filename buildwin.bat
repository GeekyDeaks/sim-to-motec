pyinstaller --noconsole --onefile ams2.py
pyinstaller --noconsole --add-data stm\gt7\db\*.csv;stm\gt7\db --onefile gt7.py
tar acvf dist\MotecWorkspace.zip MotecWorkspace