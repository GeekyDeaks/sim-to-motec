# curtesy of Bornhall
# https://github.com/Bornhall/gt7telemetry/blob/main/gt7trackdetect.py

# curl https://raw.githubusercontent.com/Bornhall/gt7telemetry/main/gt7trackdetect.csv -o stm/gt7/track/gt7trackdetect.csv 

import csv
import os
from logging import getLogger
l = getLogger(__name__)

PATH=os.path.dirname(__file__)

TRACKS = {}

with open(os.path.join(PATH, "course.csv"), "r") as fin:
    reader = csv.reader(fin)
    next(reader) # skip the head
    # ID,ShortName,Maker
    for id, name, base, *_ in reader:
        id = int(id)
        TRACKS[id] = {
            "id": id,
            "name": name,
            "base": base
        }

# load the cars
def lookup_track_name(id):
    if id in TRACKS:
        return TRACKS[id]["name"]
    else:
        return f"TRACK-{id}"
    

class TrackBounds:
	def __init__(self, **kwargs):
		for key, value in kwargs.items():
			# Convert the value to the appropriate data type
			if key in ['TRACK']:
				value = int(value)
			elif key in ['DIRECTION']:
				value = str(value)
			else:
				value = float(value)

			# Set the attribute on the instance
			setattr(self, key, value)

	def __str__(self):
		# Create a list of strings for the properties
		prop_strings = []
		for key, value in self.__dict__.items():
			prop_strings.append(f'{key}: {value} ({type(value).__name__})')
	
		# Join the strings with newlines
		return '\n'.join(prop_strings)


def load_track_bounds(filename):
	# Open the CSV file
	with open(filename, 'r') as f:
		# Read the rows from the CSV file
		rows = list(csv.DictReader(f))

	# Create a list of TrackBounds instances
	track_bounds = []
	for row in rows:
		track_bounds.append(TrackBounds(**row))

	return track_bounds


def line_intersects(p0_x, p0_y, p1_x, p1_y, p2_x, p2_y, p3_x, p3_y):

	s1_x = p1_x - p0_x
	s1_y = p1_y - p0_y
	s2_x = p3_x - p2_x
	s2_y = p3_y - p2_y

	s = (-s1_y * (p0_x - p2_x) + s1_x * (p0_y - p2_y)) / (-s2_x * s1_y + s1_x * s2_y)
	t = (s2_x * (p0_y - p2_y) - s2_y * (p0_x - p2_x)) / (-s2_x * s1_y + s1_x * s2_y)

	d = '--'
	if s2_x > 0:
		# Second set of coordinates has a positive x direction
		d = 'PX'
	elif s2_x < 0:
		# Second set of coordinates has a negative x direction
		d = 'NX'
	elif s2_y > 0:
		# Second set of coordinates has a positive y direction
		d = 'PY'
	elif s2_y < 0:
		# Second set of coordinates has a negative y direction
		d = 'NY'
	else:
		# Second set of coordinates has no discernible direction
		d = '??'

	if s >= 0 and s <= 1 and t >= 0 and t <= 1:
		# Collision detected
		return (1, d)
	return (0, d) # No collision

# ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

def get_bounding_box(x1, y1, x2, y2):
	return min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)

def get_bounding_box_area(box):
	return (box[2] - box[0]) * (box[3] - box[1])

def get_bounding_box_intersection(box1, box2):
	left = max(box1[0], box2[0])
	right = min(box1[2], box2[2])
	top = max(box1[1], box2[1])
	bottom = min(box1[3], box2[3])
	if left > right or top > bottom:
		# The bounding boxes do not overlap
		return None
	return left, top, right, bottom

def calculate_iou(outer_bounding_box, inner_bounding_box):
	# Calculate the area of the intersection of the bounding boxes
	intersection = get_bounding_box_intersection(outer_bounding_box, inner_bounding_box)
	if intersection is None:
		return 0
	intersection_area = get_bounding_box_area(intersection)
	outer_area = get_bounding_box_area(outer_bounding_box)
	inner_area = get_bounding_box_area(inner_bounding_box)
	iou = intersection_area / (outer_area + inner_area - intersection_area)
	return iou

def find_matching_track(L1X, L1Y, L2X, L2Y, MinX, MinY, MaxX, MaxY, track_bounds, max_matches=3, min_iou=0.02):
	# Calculate the outer bounding box for the line defined by L1X, L1Y, L2X and L2Y
	outer_bounding_box = get_bounding_box(MinX, MinY, MaxX, MaxY)

	# Find the elements with the highest IoUs
	matches = []
	for element in track_bounds:
		# Calculate the inner bounding box for the line defined by P1X, P1Y, P2X and P2Y
		inner_bounding_box = get_bounding_box(element.MINX, element.MINY, element.MAXX, element.MAXY)

		# Check if the lines intersect
		intersects, direction = line_intersects(element.P1X, element.P1Y, element.P2X, element.P2Y, L1X, L1Y, L2X, L2Y)
		if intersects == 0:
			# The lines do not intersect, so skip this element
			continue

		# Check if the direction of the element matches the direction of the intersection point
		if element.DIRECTION != direction:
			# The direction does not match, so skip this element
			continue

		# Calculate the IoU
		iou = calculate_iou(outer_bounding_box, inner_bounding_box)

		# The lines intersect, so add the element and its direction to the matches list
		matches.append((iou, element.TRACK))

	# Sort the matches list in descending order of IoU
	matches.sort(key=lambda x: x[0], reverse=True)

	# Return the top max_matches elements in the matches list
	if not matches:
		return None

	# Get the best match
	best_match = matches[0]

	# Filter out matches that are not within 2-3% of the best match
	filtered_matches = [match for match in matches if match[0] >= best_match[0] * (1 - min_iou)]
	if len(filtered_matches) > max_matches:
		filtered_matches = filtered_matches[:max_matches]

	return filtered_matches


class GT7TrackDetector():
	
    track_bounds = load_track_bounds(os.path.join(os.path.dirname(__file__), "gt7trackdetect.csv"))

    def __init__(self):
        self.prevLap = -1
        self.maxX = -999999.9
        self.maxY = -999999.9
        self.minX = 999999.9
        self.minY = 999999.9
        self.gotTrack = -1
        self.track = None
        self.track_name = None
        self.probability = 0.0
	
    def update(self, x, z):
	
        if x > self.maxX:
            self.maxX = x
        if x < self.minX:
            self.minX = x
        if z > self.maxY:
            self.maxY = z
        if z < self.minY:
            self.minY = z
	    
    def guess(self, x0, z0, x1, z1):
        
        matches = find_matching_track(x0, z0, x1, z1, self.minX, self.minY, self.maxX, self.maxY, GT7TrackDetector.track_bounds)
        if matches:
            if len(matches) > 1:
                l.info(f"Got {len(matches)} track matches, picking top one")

            self.probability = matches[0][0]
            self.track = matches[0][1]
            # look the track up
            self.track_name = lookup_track_name(matches[0][1])
            l.info(f"Got a {self.probability * 100:.0f}% match: [{self.track}] {self.track_name}")

		