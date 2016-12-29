Annual Fossil-Fuel CO2 Emissions: Mass of Emissions Gridded by One Degree
Latitude by One Degree Longitude

R.J. Andres and T.A. Boden

Carbon Dioxide Information Analysis Center
Environmental Sciences Division
Oak Ridge National Laboratory
Oak Ridge, Tennessee 37831-6290 U.S.A.

G. Marland
Research Institute for Environment, Energy, and Economics
Appalachian State University
Boone, NC 28608-2131 USA

DOI: 10.3334/CDIAC/ffe.ndp058.2016

Period of Record
----------------

1751-2013


Methods
-------

The basic data provided in these data files are derived from time
series of Global, Regional, and National Fossil-Fuel CO2 Emissions
(http://cdiac.ornl.gov/trends/emis/overview_2013.html) and references
therein.  The data accessible here take these tabular, national,
mass-emissions data and distribute them spatially on a one degree latitude
by one degree longitude grid.  The within-country spatial distribution is
achieved through a fixed population distribution as reported in Andres et
al. (1996) for years prior to 1990 and a variable population distribution
for later years (Andres et al. 2016).  Note that the mass-emissions data
used here are based on fossil-fuel consumption estimates as these are more
representative of within country emissions than fossil-fuel production
estimates (see http://cdiac.ornl.gov/faq.html#Q10 for a description
why emission totals based upon consumption differ from those based upon
production).

Data File Structure and Naming Convention
-----------------------------------------

There is a separate data file for each year.  The files have a basename
of gridcar and an extension of yyyy where yyyy is the year (e.g., 2000).

The unit of the mass data portrayed is 10E6 metric tonnes of C or Tg C (Tg=10E12 g).

Two identical sets of data are available;

1. Compressed gridcar.yyyy.Z files (one file for each year).  These files
were compressed using the standard unix compression utility to speed
downloading.  You will need to uncompress them using the unix "uncompress
*" command), and

2. One tar file (gridcar.tar) file which contains all 263 files in a
compressed state.  Before using the files, users will need to extract the
files from the tar file using the "tar xvf gridcar.tar" command and then
uncompress the resulting files using the unix "uncompress *" command.

We suggest the data should be plotted before directly incorporating the
data into a model or other use.  If read in correctly, the data should
plot a map of the world with North at the top and East to the right. On
each line, the data go from the 180-179 degrees west cell to the 179-180
degrees east cell until reading in the next line of data. In FORTRAN,
the data were written with:

parameter (maxlat=180, maxlon=360)

C DISTRIBUTE C ON GRID
do 1200, i=1, maxlat
do 1200, j=1, maxlon
write (14, 1310) gridcar (i,j)
1200 continue
1310 format (ES13.6E2)

In addition to the annual gridcar.* files, there is one SUMMARY.MASS.DAT
file.  This summary file contains the year, minimum grid cell value,
maximum grid cell value, and sum of the grid cell values.  This file is
included as an additional means to check that the gridcar.* files have
been read correctly.


Reference
---------

Andres RJ, Marland G, Fung I, Matthews E (1996) A one degree by
one degree distribution of carbon dioxide emissions from fossil fuel
consumption and cement manufacture, 1950-1990. Global Biogeochem. Cycles
10:419-429. doi:10.1029/96GB01523.

Andres RJ, Boden TA, Higon DM (2016) Gridded uncertainty
in fossil fuel carbon dioxide emission maps, a CDIAC
example. Atmos. Chem. Phys. Discuss. doi:10.5194/acp-2016-258.

CITE AS: Andres, R.J., T.A. Boden, and G. Marland. 2016.  Annual
Fossil-Fuel CO2 Emissions: Mass of Emissions Gridded by One Degree
Latitude by One Degree Longitude.  Carbon Dioxide Information Analysis
Center, Oak Ridge National Laboratory, U.S. Department of Energy, Oak
Ridge, Tenn., U.S.A.  doi 10.3334/CDIAC/ffe.ndp058.2016
