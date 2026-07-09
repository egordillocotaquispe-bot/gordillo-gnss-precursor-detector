# GNSS Data

This folder contains the `.tenv3` files of the GNSS stations used in the validation of the algorithm.

The files are not included in this repository due to their size. They must be downloaded from the Nevada Geodetic Laboratory (NGL).

## Stations used

| Code   | Location               | Data period   |
|--------|------------------------|---------------|
| AREQ   | Arequipa, Peru         | 1994 - present |
| CRBR   | Peru                   | 2008 - 2014   |
| TQPL   | Peru                   | 2009 - 2014   |
| IQQE   | Iquique, Chile         | 2010 - present |
| PSGA   | Pisagua, Chile         | 2010 - present |
| AEDA   | Chile                  | 2010 - present |
| ATJN   | Chile                  | 2010 - present |
| CRSC   | Chile                  | 2010 - present |

## How to download the data

1. Go to the Nevada Geodetic Laboratory website:  
   https://geodesy.unr.edu/

2. Search for the station by its code (e.g., AREQ).

3. Download the corresponding `.tenv3` file.

4. Place the file in this folder (`data/`).

## Expected file format

The `.tenv3` files must follow the standard NGL format. The columns used by the algorithm are:

- `YYMMMDD` : date in YYMMMDD format (e.g., 94FEB01)
- `__height(m)` : vertical component of deformation in meters

## Attribution and citation

The GNSS data used in this project are provided by the Nevada Geodetic Laboratory (NGL), University of Nevada, Reno.

When using these data, you must cite:

Blewitt, G., W. C. Hammond, and C. Kreemer (2018), Harnessing the GPS data explosion for interdisciplinary science, Eos, 99, https://doi.org/10.1029/2018EO104623.

Additionally, proper attribution should be given to the original data providers and sponsors of each station, as specified by the NGL.

## Notes

- If you do not have access to the data, you may request them through the NGL portal or contact the author of this project.
- The algorithm expects the files to be in the standard NGL `.tenv3` format. No preprocessing is required.