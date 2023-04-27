# AUTHOR:		Kate McCarthy (kem6ur@virginia.edu, kemccarthy6@gmail.com)
# CREATED: 		November 2022 (Last modified April 2023)
# DESCRIPTION:	Downloads MOLA DEM and SHARAD radargram, cluttergram, and geom table for a given orbit.

import requests
import cv2
import argparse
import os

parser = argparse.ArgumentParser(
                    prog='download_files',
                    description='Downloads SHARAD radargram, cluttergram, and geom table for a specified orbit.')
parser.add_argument('-o', '--orbit')
args = parser.parse_args()
orbit_str = args.orbit

orbit_str = orbit_str.zfill(8)
first_4_digits = str(orbit_str)[:4]

# Set up initial directory structure if needed
paths = ['./downloads/SHARAD/images/radargrams', './downloads/SHARAD/images/cluttergrams', './downloads/SHARAD/geom','./downloads/MOLA']
for path in paths:
	if not os.path.exists(path):
		os.makedirs(path)

# Download MOLA DEM if not already downloaded
mola_dem = './downloads/MOLA/Mars_MGS_MOLA_DEM_mosaic_global_463m.tif'
if not os.path.exists(mola_dem):
	mola_dem_URL = 'https://planetarymaps.usgs.gov/mosaic/Mars_MGS_MOLA_DEM_mosaic_global_463m.tif'
	response = requests.get(mola_dem_URL)
	open(mola_dem, "wb").write(response.content)

# Get radargram
radargram_file_name = "./downloads/SHARAD/images/radargrams/s_" + orbit_str + ".tif"
radargram_URL = "https://pds-geosciences.wustl.edu/mro/mro-m-sharad-5-radargram-v2/mrosh_2101/browse/tiff/s_" + first_4_digits + "xx/s_" + orbit_str + "_tiff.tif"
response = requests.get(radargram_URL)
open(radargram_file_name, "wb").write(response.content)
# Convert gray image to color format so that radargram can be annotated.
gray = cv2.imread(radargram_file_name)
backtorgb = gray[:,:,::-1]
cv2.imwrite(radargram_file_name, backtorgb)

# Get cluttergram
cluttergram_file_name = "./downloads/SHARAD/images/cluttergrams/s_" + orbit_str + ".tif"
cluttergram_URL = "https://pds-geosciences.wustl.edu/mro/urn-nasa-pds-mro_sharad_simulations/browse/s_" + first_4_digits + "xx/s_" + orbit_str + "/s_" + orbit_str + "_browse_combined.tif"
response = requests.get(cluttergram_URL)
open(cluttergram_file_name, "wb").write(response.content)

# Get geometry table
geom_file_name = "./downloads/SHARAD/geom/s_" + orbit_str + "_geom.csv"
geom_URL = "https://pds-geosciences.wustl.edu/mro/mro-m-sharad-5-radargram-v2/mrosh_2101/data/geom/s_" + first_4_digits + "xx/s_" + orbit_str + "_geom.tab"
response = requests.get(geom_URL)
open(geom_file_name, "wb").write(response.content)
