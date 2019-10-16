# extract_asisdata
Process inputs for modeling seabeach amaranth habitat at Assateague Island 

In development. The iPython notebook is where everything is happening now. I started in the python file (beachplant_extractor.py), but then moved over to sa_extraction.ipynb. 

Related to: https://github.com/esturdivant-usgs/BI-geomorph-extraction

#### How Emily runs this on Windows 10 with ArcGIS Pro 2.0: 

The only way I know to access the ArcPy module outside of an ArcGIS GUI, is to activate the conda environment installed with ArcGIS Pro. In the bash console, type `\ArcGIS\Pro\bin\Python\Scripts\proenv` to activate the ArcGIS Pro Python 3 conda environment. Then open a jupyter lab session: `jupyter lab`. You may need to install some additional Python packages, such as jupyterlab (`conda install -c conda-forge jupyterlab`). 

In bash console:

```
\ArcGIS\Pro\bin\Python\Scripts\proenv
jupyter lab 
```

Once in jupyter lab, navigate to the location of this repository and open the notebook file sa_extraction.ipynb.
