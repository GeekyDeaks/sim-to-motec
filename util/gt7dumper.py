# crude script to dump raw UDP packets from GT7 to an sqlite DB for later analysis
# files get written to logs/raw/gt7-samples-[TIMESTAMP].db

import socket
import sys
import datetime
import time
import sqlite3
import os

PATH = "logs/raw"
os.makedirs(PATH, exist_ok=True)

rx_port = 33740
tx_port = 33739

if len(sys.argv) == 2:
    # Get "IP address of Server" and also the "port number" from
    ip = sys.argv[1]
else:
    print("Usage: python gt7dumper.py <playstation-ip>")
    exit(1)

###
# Create a UDP socket for the inbound packets
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Bind to any address
server_address = ('0.0.0.0', rx_port)
s.bind(server_address)
s.settimeout(10)

isodate = datetime.datetime.now().replace(microsecond=0).isoformat().replace('-', '').replace(':', '')
con = sqlite3.connect(os.path.join(PATH, f"gt7-samples-{isodate}.db") )
cur = con.cursor()
cur.execute("CREATE TABLE samples(timestamp int, data blob)")

def send_hb(s):
  send_data = 'A'.encode('utf-8')
  s.sendto(send_data, (ip, tx_port))

send_hb(s)
print("Ctrl+C to exit the program")

pkt_count = 0
print("waiting for GT7")

while True:
    try:
        data, address = s.recvfrom(4096)

        timestamp = int(time.time() * 1000)

        cur.execute("INSERT INTO samples(timestamp, data) VALUES (?, ?)", (timestamp, data))
        
        # GT7 sends a packet per tick which is about 60hz
        if (pkt_count % 600) == 0 and pkt_count > 0:
            print(f"processed {pkt_count} UDP packets")
            con.commit()

        if (pkt_count % 100) == 0:
            send_hb(s)

        pkt_count += 1

    except KeyboardInterrupt:
        print('stopping')
        con.commit()
        break

    except Exception as e:
        print(e, "- waiting again for GT7")
        send_hb(s)
        next_sample = 0 # reset the sample points

con.close()