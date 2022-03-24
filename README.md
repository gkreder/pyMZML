# pyMZML


## Installation

From inside the top package directory run 

``` bash
pip install .
```

## Create Output Directory with Indvidual Tsv Files

specIndices.txt contains only spectrum indices (no header)

``` bash
pyMZML.py tsvs "051-075.mzML" "specIndices.txt" "testOutDirectory"
```

## Create Intensity Matrix From Filtered MZs List

specIndices.txt contains only spectrum indices (no header). Mzs.txt contains only mzs (no header)

``` bash
pyMZML.py mzFiltered "051-075.mzML" "specIndices.txt" "mzs.txt" "testOut.tsv"
```


## Create Intensity Matrices From Filtered MZs List and input Tsv

Each row in multiMzInput.tsv starts with an mzml file name (absolute path to the file) then each subsequent cell in the row is a spectrum index of interest. Rows can be variable length. specIndices.txt contains only spectrum indices (no header). Mzs.txt contains only mzs (no header)

``` bash
pyMZML.py "multiMzFiltered" "multiMzInput.tsv" "mzs.txt" "testOutDirectory"
```

