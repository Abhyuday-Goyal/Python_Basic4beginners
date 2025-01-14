import sys
import numpy as np
import os.path

from subprocess import call
from pyhdf.SD import SD, SDC
import h5py
from netCDF4 import Dataset

import matplotlib.colors as cls
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator, FixedLocator, MultipleLocator

import cartopy.crs as ccrs
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import cartopy.feature as cfeature
import shapely.geometry as sgeom

from scipy.interpolate import griddata

from sklearn import linear_model

from scipy.stats import kde


print("Sucess if no errors!")
