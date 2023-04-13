# Kate McCarthy (kem6ur@virginia.edu)
# Advanced Remote Sensing Spring 2023
# Given the location and depth of reflector points, generates a plot of reflector geometry overlaid on a MOLA elevation profile.

# References:
#  MOLA DEM - https://astrogeology.usgs.gov/search/map/Mars/GlobalSurveyor/MOLA/Mars_MGS_MOLA_DEM_mosaic_global_463m
#  NumPy documentation - https://numpy.org/doc/stable/index.html
#  Rasterio example with MOLA - https://towardsdatascience.com/terraforming-mars-with-python-4c21ed75117f
#  Martian Coordinate Systems - https://ode.rsl.wustl.edu/mars/pagehelp/Content/Frequently_Asked_Questions/Coordinate_System.htm

import rasterio
import numpy as np
import matplotlib.pyplot as plt

# Converts coordinate pair to an image pixel on a hypothetical map of mars, where each pixel is 1 degree.
# Returns (p_x, p_y) pixel index from the top left corner. Images are a 2D array of pixels in row-major order, so p_x must start from the left side of the map and p_y must go from the top down.
#	x:					x coordinate.
#	y:					y coordinate.
#	x_ew (optional):	"w" for West of Mars' prime meridian. Alternatively, pass in a negative x-coordinate.
#	y_ns (optional):	"s" for South of Mars' equator. Alternatively, pass in a negative y-coordinate.
def convert_map_coordinates_to_pixel_index(x, y, x_ew="", y_ns=""):

	if x_ew == "w" or x < 0:
		p_x = 180 - abs(x)
	else: 
		p_x = 180 + x

	if y_ns == "s" or y < 0:
		p_y = 90 + abs(y)
	else:
		p_y = 90 - abs(y)

	return (p_x, p_y)

# Converts pixel index (p_x, p_y) to an image pixel on MOLA DEM by multiplying by MOLA scaling factor.
def scale_pixel_index_for_mola(p_x, p_y):
	return (int(p_x * 128), int(p_y * 128))

# Returns longitude on Mars given a scaled pixel's x index. Used for labeling plot's x axis.
def get_lon_from_scaled_pixel_index(x):
	
	# remove MOLA scaling factor
	unscaled_x = x/128
	
	# convert from unscaled pixel index to Mars x coordinate
	unconverted_x = unscaled_x - 180

	return unconverted_x

# Returns latitude on Mars given a scaled pixel's y index. Used for labeling plot's y axis.
def get_lat_from_scaled_pixel_index(y):

	unscaled_y = y/128 # remove MOLA scaling factor

	 # convert from unscaled pixel index to Mars y coordinate
	if unscaled_y <= 90: # point on or above Mars' equator
		unconverted_y = abs(unscaled_y - 90)

	else: # point below Mars' equator
		unconverted_y = ((unscaled_y) - 90) * -1

	return unconverted_y

# Given the equation of a line and either the x or y coordinates of 2 endpoints, returns a list of points along the line.
#	m:			slope of line.
#	b:			y-intercept of line.
#	coord1:		either x1 or y1.
#	coord2:		x2 if x1 was passed in, or y2 if y1 was passed in.
#	x_or_y:		"x" if x coordinates were passed in or "y" if y coordinates were passed in.
def get_points_on_line(m, b, coord1, coord2, x_or_y):

	c_max = max(coord1, coord2)
	c_min = min(coord1, coord2)

	points_on_line = []

	# add each coord between c1 and coord2 (inclusive) to the list.
	if x_or_y == "x":
		for x in range(c_min, (c_max + 1)):
			y = int(m * x + b)
			if not [x, y] in points_on_line:
				points_on_line.append([x, y])
	else:
		for y in range(c_min, (c_max + 1)):
			x = int((y - b)/m)
			if not [x, y] in points_on_line:
				points_on_line.append([x, y])

	return points_on_line

# Returns a list of points along a line between 2 points (x1, y1) and (x2, y2). 
# The 2 points must be in scaled pixel index format.
def get_line_from_point_pair(point1, point2):
	x1 = point1[0]
	y1 = point1[1]
	x2 = point2[0]
	y2 = point2[1]

	points_on_line = []
	
	if (x2 - x1) != 0: # if the line is not vertical

		# calculate slope of line
		m = (y2 - y1) / (x2 - x1)
		# calculate y-intercept of line
		b = y1 - (m * x1)

		# determine whether difference in x coords > difference in y coords
		coord1 = x1
		coord2 = x2
		x_or_y = "x"
		
		if abs(y1 - y2) > abs(x1 - x2):
			coord1 = y1
			coord2 = y2
			x_or_y = "y"

		# get the points along the line and their map coordinates
		points_on_line = get_points_on_line(m, b, coord1, coord2, x_or_y)

	else: # handle "no slope" case (vertical line)
		m = None
		b = None

		for y in range(min(y1, y2), (max(y1, y2) + 1)):
			if not [x1, y] in points_on_line:
				points_on_line.append([x1, y])

	return points_on_line

# Generates a plot of reflector geometry overlaid on a MOLA elevation profile.
#	point1:				A planetocentric coordinate pair [x, y] representing one endpoint of a line on a map of Mars.
#	point2:				A planetocentric coordinate pair [x, y] representing the other endpoint of a line on a map of Mars.
#	reflector_points:	A list of elements to plot, with each element in the format: [lon, lat, depth_from_surface, color]
#	plot_title:			The title to display above the plot.
def create_plot(point1, point2, reflector_points, plot_title):
	
	# Open MOLA DEM. Downloaded MOLA DEM from: https://astrogeology.usgs.gov/search/map/Mars/GlobalSurveyor/MOLA/Mars_MGS_MOLA_DEM_mosaic_global_463m
	mars = rasterio.open('./downloads/MOLA/Mars_MGS_MOLA_DEM_mosaic_global_463m.tif')
	mars = mars.read()

	# Convert the point coordinates to pixel indices.
	(converted_x1, converted_y1) = convert_map_coordinates_to_pixel_index(point1[0],point1[1])
	(converted_x2, converted_y2) = convert_map_coordinates_to_pixel_index(point2[0],point2[1])

	# Scale pixel indices for MOLA DEM.
	(scaled_x1, scaled_y1) = scale_pixel_index_for_mola(converted_x1, converted_y1)
	(scaled_x2, scaled_y2) = scale_pixel_index_for_mola(converted_x2, converted_y2)
	scaled_point1 = [scaled_x1, scaled_y1]
	scaled_point2 = [scaled_x2, scaled_y2]

	# Get the points along the line between the two points.
	line_points = get_line_from_point_pair(scaled_point1, scaled_point2) #[[scaled_point1[0], scaled_point1[1]], [scaled_point2[0], scaled_point2[1]]]#get_line_from_point_pair(scaled_point1, scaled_point2)

	# determine if x axis should show lat or lon.
	lat_or_lon = "lon"
	
	# handle if difference in y coordinates is greater than difference in x coordinates.
	if abs(scaled_point1[1] - scaled_point2[1]) > abs(scaled_point1[0] - scaled_point2[0]):
		lat_or_lon = "lat"

	altitude_profile = [] # altitude values at each point in the line.
	lat_or_lon_coords = [] # corresponding lat or lon coordinates at each point in the line.
	x_axis_title = "" # the title for the plot's x axis (either latitude or longitude).  

	for point in line_points:

		# Get the altitude at a specific pixel.
		altitude = (mars[0])[point[1]][point[0]] # must be in [y][x] order because arrays are stored in row-major order.
		altitude_profile.append(altitude)
		if lat_or_lon == "lon":
			lon_coord = get_lon_from_scaled_pixel_index(point[0])
			lat_or_lon_coords.append(lon_coord)
			x_axis_title = "Longitude"
		else:
			lat_coord = get_lat_from_scaled_pixel_index(point[1])
			lat_or_lon_coords.append(lat_coord)
			x_axis_title = "Latitude"


	altitude_profile_np = np.array(altitude_profile)
	lat_or_lon_coords_np = np.array(lat_or_lon_coords)
	plt.plot(lat_or_lon_coords_np, altitude_profile_np, color='black')

	for point in reflector_points:
		
		(converted_x, converted_y) = convert_map_coordinates_to_pixel_index(point[0],point[1])
		(scaled_x, scaled_y) = scale_pixel_index_for_mola(converted_x, converted_y)

		altitude = (mars[0])[scaled_y][scaled_x] - point[2]
		lat = get_lat_from_scaled_pixel_index(scaled_y)

		plt.plot(lat, altitude, marker='.', color=point[3], ls='none', ms=10)

	plt.xlabel(x_axis_title, fontdict={'fontsize': 12})
	plt.ylabel('Elevation (m)', fontdict={'fontsize': 12}) 

	plt.title(plot_title, fontdict={'fontsize': 18})

	plt.show()
