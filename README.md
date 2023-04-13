# Ice-Filled Craters on Mars
Kate McCarthy | Advanced Remote Sensing Project, Spring 2023
<br/>
## Contents
- [Guide](#guide)
- [Dependencies](#dependencies)
<br/>

## <a name="guide"></a>Guide to plotting SHARAD reflector geometry on top of a MOLA elevation profile assuming different dielectric constants

### 1. Run download_SHARAD_data.py with a specific SHARAD orbit number.
For example, to download data from SHARAD orbit 1308401, enter the following command:
```
python3 download_SHARAD_data.py -o 1308401
```

### 2. Compare the radargram and cluttergram. Trace the surface and any potential reflectors using the colors listed below.
The radargram is located in `./downloads/SHARAD/images/radargrams/`. The cluttergram is located in `./downloads/SHARAD/images/cluttergrams/`.
- The estimated **surface of Mars** must be traced on the radargram in **yellow** `(B:0, G:255, R:255)`
- Potential reflectors (subsurface reflectors not present in the cluttergram) can be traced on the radargram in any of the following colors (use these exact RGB values):
  - red `(B:0, G:0, R:255)`
  - blue `(B:255, G:0, R:0)`
  - green `(B:0, G:255, R:0)`
  - magenta `(B:255, G:0, R:255)`
  - cyan `(B:255, G:255, R:0)`
  - mediumslateblue `(B:255, G:129, R:122)`
  - steelblue `(B:180, G:130, R:70)`
  - moccasin `(B:181, G:228, R:255)`
  
### 3. Run plot_refl_geom_from_annotated_rdg.py with the orbit number of your annotated SHARAD radargram.
For example, to plot reflector geometry for SHARAD orbit 1308401 on a MOLA evelation profile, enter the following command:
```
python3 plot_refl_geom_from_annotated_rdg.py -o 1308401
```
This will generate two different plots of reflector geometry overlaid on a MOLA elevation profile. One assumes that the dielectric constant of the subsurface is 1 (a vacuum), and another assumes the dielectric constant of the subsurface is 3.1 (approximate value for water ice on Mars).
<br/>

## <a name="dependencies"></a>Dependencies
- [opencv-python](https://pypi.org/project/opencv-python/)
- numpy
- pandas
- matplotlib
- scipy
- rasterio
- argparse
- requests
