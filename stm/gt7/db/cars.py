import csv
import os

PATH=os.path.dirname(__file__)

CARS = {}

with open(os.path.join(PATH, "cars.csv"), "r") as fin:
    reader = csv.reader(fin)
    next(reader) # skip the head
    # ID,ShortName,Maker
    for id, name, maker in reader:
        id = int(id)
        CARS[id] = {
            "id": id,
            "name": name,
            "maker": maker
        }

# load the cars
def lookup_car_name(id):
    if id in CARS:
        return CARS[id]["name"]
    else:
        return f"CAR-{id}"
