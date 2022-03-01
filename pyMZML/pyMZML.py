################################################################################
"""pyMZML

Usage:
  pyMZML.py tsvs <mzMLIn> <spectrumIndices> <outDirectory>
  pyMZML.py mzFiltered <mzMLIn> <spectrumIndices> <mzs> <outTsv> [--tolerance=<tol>]
  pyMZML.py (-h | --help)
  pyMZML.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.
  --tolerance=<tol>  m/z matching tolerance [default: 0.01].
"""
################################################################################
import sys
import os
from tqdm.auto import tqdm
import numpy as np
from docopt import docopt
from pyopenms import *
################################################################################

def readTxt(spectrumIndices):
    with open(spectrumIndices, 'r') as f:
        sids = [x.strip() for x in f.readlines()]
    sids = [x for x in sids if x != '']
    return(sids)

def singleFiles(mzMLIn, spectrumIndices, outDirectory):
    print("Starting singleFiles output...")
    os.system(f"mkdir -p {outDirectory}")
    ode = OnDiscMSExperiment()
    ode.openFile(mzMLIn)
    sids = readTxt(spectrumIndices)
    for sid in tqdm(sids):
        sid = int(sid)
        spec = ode.getSpectrum(sid)
        s_mzs, s_ints = spec.get_peaks()
        with open(os.path.join(outDirectory, f"{sid}.tsv"), "w") as f:
            print(f"m/z\tIntensity", file = f)
            for mz, intensity in zip(s_mzs, s_ints):
                print(f"{mz}\t{intensity}", file = f)
    print("Done")

    
def mzFiltered(mzMLIn, spectrumIndices, outTsv, mzs, tol):
    print("Starting mzFiltered output...")
    tol = float(tol)
    ode = OnDiscMSExperiment()
    ode.openFile(mzMLIn)
    sids = readTxt(spectrumIndices)
    mzs = readTxt(mzs)
    outCols = []
    for sid in tqdm(sids):
        outCol = []
        sid = int(sid)
        spec = ode.getSpectrum(sid)
        s_mzs, s_ints = spec.get_peaks()
        for rmz in mzs:
            rmz = float(rmz)
            hitIdxs = np.where(np.abs(rmz - s_mzs) < tol)[0]
            hits = sorted(zip(s_mzs[hitIdxs], s_ints[hitIdxs]), key = lambda x : x[1], reverse = True)
            if len(hits) == 0:
                outCol.append("")
            else:
                hmz, hintensity = hits[0]
                outCol.append(hintensity)
        outCols.append(outCol)
    with open(outTsv, 'w') as f:
        stemp = '\t'.join([str(x) for x in sids])
        print(f"m/z\t{stemp}", file = f)
        for i_mz, mz in enumerate(mzs):
            stemp = f"{mz}"
            for i_col, col in enumerate(outCols):
                stemp += f"\t{col[i_mz]}"
            print(stemp, file = f)
    print("Done")
    
def main():
    args = docopt(__doc__, version='pzMZML 0.1')
    # sys.exit(args)
    if args["tsvs"]:
        singleFiles(args["<mzMLIn>"], args["<spectrumIndices>"], args["<outDirectory>"])
    if args["mzFiltered"]:
        mzFiltered(args["<mzMLIn>"], args["<spectrumIndices>"], args["<outTsv>"], args["<mzs>"], args["--tolerance"])
    
################################################################################

if __name__ == '__main__':
    main()

