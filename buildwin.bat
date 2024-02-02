pyinstaller --noconsole --add-data stm\ams2\tracks\*.json;stm\ams2\tracks --onefile ams2.py
pyinstaller --noconsole --add-data stm\gt7\db\*.csv;stm\gt7\db --onefile gt7.py 