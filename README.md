# extract_asisdata
Extract data at Assateague Island for Seabeach Amaranth habitat modeling

In development. The iPython notebook is where everything is happening now. Got started in the python file, but not working there now. 

Related to: https://github.com/esturdivant-usgs/BI-geomorph-extraction

How Emily runs this on Windows 10 with ArcGIS Pro 2.0: 

In the bash console, type `\ArcGIS\Pro\bin\Python\Scripts\proenv` to activate the ArcGIS Pro Python 3 conda environment. This is the only way I know to access ArcPy outside of an ArcGIS GUI. Change directories into the location of this code: `cd Code\beachplant_dataextraction` Then open a jupyter lab session: `jupyter lab`. At the beginning, you may need to install some additional Python packages, such as jupyterlab (`conda install -c conda-forge jupyterlab`). 

In bash console: 

```
# Activate ArcGIS Pro Python 3 conda environment
\ArcGIS\Pro\bin\Python\Scripts\proenv 
# Open a jupyter lab session
jupyter lab
```
