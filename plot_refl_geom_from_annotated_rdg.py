# Kate McCarthy (kem6ur@virginia.edu)
# Advanced Remote Sensing Spring 2023
# Identifies surface pixels and reflector pixels drawn on a SHARAD radargram. 
# Then, calls plot_topo_profile_with_reflector.py to plot the reflectors assuming different dielectric constants on top of a MOLA elevation profile.

# NOTES FOR USE:
# Estimated surface of Mars must be traced on the radargram in yellow (B:0, G:255, R:255). 
# Reflectors can be traced on the radargram in any of the following colors:
# 	- red (B:0, G:0, R:255)
#	- blue (B:255, G:0, R:0)
# 	- green (B:0, G:255, R:0)
#	- magenta (B:255, G:0, R:255)
#	- cyan (B:255, G:255, R:0)
#	- mediumslateblue (B:255, G:129, R:122)
#	- steelblue (B:180, G:130, R:70)
#	- moccasin (B:181, G:228, R:255)

import cv2
import numpy as np
import csv
import pandas
import plot_topo_profile_with_reflector as mola_plotter
import matplotlib.pyplot as plt
import copy
from scipy import constants 
import math
import argparse

parser = argparse.ArgumentParser(
                    prog='download_files',
                    description='Downloads SHARAD radargram, cluttergram, and geom table for a specified orbit.')
parser.add_argument('-o', '--orbit')
args = parser.parse_args()
orbit_str = args.orbit
orbit_str = orbit_str.zfill(8)

# take in annotated radargram
img = cv2.imread("./downloads/SHARAD/images/radargrams/s_" + orbit_str + ".tif")

points = []
surface_coordinates = {}
coordinates_by_color = []

# Identify surface and reflector pixels by color
# color range format: (B, G, R)
yellow_pixels = np.argwhere(cv2.inRange(img, (0, 250, 250), (0, 255, 255)))
print("yellow pixels", yellow_pixels)

red_pixels = np.argwhere(cv2.inRange(img, (0, 0, 250), (0, 0, 255)))
print("red_pixels", red_pixels)

blue_pixels = np.argwhere(cv2.inRange(img, (250, 0, 0), (255, 0, 0)))
print("blue pixels", blue_pixels)

green_pixels = np.argwhere(cv2.inRange(img, (0, 250, 0), (0, 255, 0)))
print("green pixels", green_pixels)

magenta_pixels = np.argwhere(cv2.inRange(img, (250, 0, 250), (255, 0, 255)))
print("magenta pixels", magenta_pixels)

cyan_pixels = np.argwhere(cv2.inRange(img, (250, 250, 0), (255, 255, 0)))
print("cyan pixels", cyan_pixels)

mediumslateblue_pixels = np.argwhere(cv2.inRange(img, (255, 129, 122), (255, 129, 122)))
print("mediumslateblue pixels", mediumslateblue_pixels)

steelblue_pixels = np.argwhere(cv2.inRange(img, (180, 130, 70), (180, 130, 70)))
print("steelblue pixels", steelblue_pixels)

moccasin_pixels = np.argwhere(cv2.inRange(img, (181, 228, 255), (181, 228, 255)))
print("moccasin pixels", moccasin_pixels)

pixels_by_color = [red_pixels,blue_pixels,green_pixels,magenta_pixels,cyan_pixels,mediumslateblue_pixels,steelblue_pixels,moccasin_pixels]
color_names = ["red", "blue", "green", "magenta", "cyan", "mediumslateblue","steelblue","moccasin"]

# record pixel coordinates of different reflectors by color
for pixel_color in pixels_by_color:
	coordinates = {}
	for py, px in pixel_color:
	    coordinates[px] = py
	coordinates_by_color.append(coordinates)

# record pixel coordinates of the estimated surface
for py, px in yellow_pixels:
    surface_coordinates[px] = py

reflector_points_depth_corrected = []
reflector_points_vacuum = []

# grab lat & lon of each radargram frame from the orbit's geometry table
with open('./downloads/SHARAD/geom/s_' + orbit_str + '_geom.csv') as geom:
	reader = csv.reader(geom, delimiter=',')

	radargram_frame = 0
	for row in reader:
		radargram_frame += 1

		lat = row[2]
		lon = row[3]

		if float(lon) > 180:
			lon = float(lon) - 180 - 180

		points.append([float(lon), float(lat)])

		for i in range(0, len(coordinates_by_color)):

			coordinates = coordinates_by_color[i]
			color_name = color_names[i]

			if not coordinates.get(radargram_frame) == None: # if this frame has highlighted reflector
				reflector_pixel_depth = coordinates.get(radargram_frame)

				if not surface_coordinates.get(radargram_frame) == None: # if this frame has surface highlighted
					surface_pixel_depth = surface_coordinates.get(radargram_frame)

					delta_p = reflector_pixel_depth - surface_pixel_depth # difference in radargram pixel depth between surface and reflector

					delta_t = delta_p * (0.0375/2) # delay in microsec (one-way travel time)

					speed_of_light_microsec = constants.c/1000000 # speed of light in microseconds

					in_vacuum = delta_t * (speed_of_light_microsec) 

					reflector_points_vacuum.append([float(lon), float(lat), in_vacuum, color_name])

					delta_x = delta_t * (speed_of_light_microsec / math.sqrt(3.1))# elevation diff (m) assuming dielectric constant of 3.1

					reflector_points_depth_corrected.append([float(lon), float(lat), delta_x, color_name])

# get endpoints (can adjust these to zoom in on a subsection of the radargram groundtrack as desired)
point1 = points[0]
point2 = points[len(points) - 1]

vacuum_plot_title = "SHARAD orbit " + str(int(orbit_str)) + " reflector geometry on MOLA elevation profile (\u03B5r = 1)"
mola_plotter.create_plot(point1, point2, reflector_points_vacuum, vacuum_plot_title)

depth_plot_title = "SHARAD orbit " + str(int(orbit_str)) + " reflector geometry on MOLA elevation profile (\u03B5r = 3.1)"
mola_plotter.create_plot(point1, point2, reflector_points_depth_corrected, depth_plot_title)
