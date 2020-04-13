# CologneProtocolQGIS

## Research compendium for "Approaching Prehistoric Demography: Proxies, Scales and Scope of the Cologne Protocol in European contexts"

### Compendium DOI:

**DOI will be created by figshare upon final publication**

The file linked above is connected to the publication and represents the version of the manual at that time. The files of this repository are the development versions and may have changed since the paper was published.

### Authors of this repository:

Robin Peters (mail@robinpeters.net)

### Published in:

Schmidt, I., Hilpert, J., Kretschmer, I., Peters, R., Broich, M., Schiesberg, S., Vogels, O., Wendt, K. P., Zimmermann, A., Maier, A., **submitted**. Approaching Prehistoric Demography: Proxies, Scales and Scope of the Cologne Protocol in European contexts. _Philosophical Transactions B_.

### Contents:

- Manual `CGN_Protocol_QGIS_Manual.pdf` on the stepwise and scripted processing of the **Cologne Protocol**.
- The `model\` directory contains the Python (`.py`) and R  (`.rsx`) scripts for the application of the **Cologne Protocol** in QGIS.

### Overview:

The **Cologne Protocol** is a geostatistical approach for estimating prehistoric population size and density.  
This repository contains a manual on how to model Core Areas with `QGIS` and `SAGA`. This modelling approach constitutes the first of two successive tasks within the 'Cologne Protocol' to estimate past population sizes and densities, described in more detail elsewhere (*Schmidt et al. 2020: S2.1. and S2.2.*).
`CGN_Protocol_QGIS_Manual.pdf` outlines the technical implementation of working steps 1 to 11 (see *Schmidt et al. 2020: Table S2*): You can either execute the task stepwise by hand (see manual) or use the semi-automatic scripts available in this GitHub Repository. The scripts are however experimental and manual and scripts come without any kind of guarantee, so please make sure to double-check your results. Regardless of what approach you choose, please read the publication and supplement (*Schmidt et al. 2020*) and consult the manual.

Step 1-5 of the Cologne Protocol can be performed in QGIS (`Pre-Processing.py`), building the semivariogram is either done in SAGA or using an QGIS R-script (`Variogram.rsx`). For kriging we use a SAGA function or call this function from QGIS (`Kriging.py`). Post-processing, e.g. creating contour lines and calculating the area and number of sites per isoline (Step 8-11) should be performed in SAGA as well or by using the `Post-Processing.py` from within QGIS. In short, the manual approach requires using QGIS and SAGA, is more flexible but can be tiring while the models and scripts can all be run from QGIS, do save time but require R to be installed as well.


### How to use

- It is recommended to read the publication and supplement (*Schmidt et al. 2020*) first and then to start with the example application described in the `CGN_Protocol_QGIS_Manual.pdf`.


### Other resources

There exist other manuals and recourses to fulfill the first two parts of the **Cologne Protocol**. The above mentioned publications is not only accompanied by an `QGIS` manual but also by manuals for `R`, `MapInfo` and `ArcGIS`. Please see the publication for more information.  


### Licence:

Code: MIT (http://opensource.org/licenses/MIT) year: 2020, copyright holder: Robin Peters


### Program Versions required:

The scripts were developed using QGIS 3.10, SAGA 2.3.1 and R 3.6.2.

