################################################################################
"""pyMZML

Usage:
  pyMZML.py tsvs <mzMLIn> <spectrumIndices> <outDirectory> [--noMS2Filter]
  pyMZML.py mzFiltered <mzMLIn> <spectrumIndices> <mzs> <outTsv> [--tolerance=<tol>] [--noMS2Filter]
  pyMZML.py multiMzFiltered <inTsv> <mzs> <outDirectory> [--tolerance=<tol>] [--noMS2Filter]
  pyMZML.py (-h | --help)
  pyMZML.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.
  --tolerance=<tol>  m/z matching tolerance [default: 0.01].
  --noMS2Filter  Turn off the filter checking if a spectrum is MS2 or not
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

def singleFiles(mzMLIn, spectrumIndices, outDirectory, filterMS2 = True):
    print("Starting singleFiles output...")
    os.system(f"mkdir -p {outDirectory}")
    ode = OnDiscMSExperiment()
    ode.openFile(mzMLIn)
    sids = readTxt(spectrumIndices)
    for sid in tqdm(sids):
        sid = int(sid)
        spec = ode.getSpectrum(sid)
        if filterMS2 and (spec.getMSLevel() != 2):
            print(f"Spectrum {sid} in {mzMLIn} had MS Level {spec.getMSLevel()}...it will be skipped")
            continue
        s_mzs, s_ints = spec.get_peaks()
        with open(os.path.join(outDirectory, f"{sid}.tsv"), "w") as f:
            print(f"m/z\tIntensity", file = f)
            for mz, intensity in zip(s_mzs, s_ints):
                print(f"{mz}\t{intensity}", file = f)
    print("Done")

def getOutCol(sid, ode, mzs, mzMLIn, tol, filterMS2 = True):
    outCol = []
    sid = int(sid)
    spec = ode.getSpectrum(sid)
    msl = spec.getMSLevel()
    if filterMS2 and (msl != 2):
        print(f"Spectrum {sid} in {mzMLIn} had MS Level {spec.getMSLevel()}...it will be skipped")
        return([f"MS{msl} spectrum" for x in mzs])
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
    return(outCol)


def writeOutTsv(outTsv, sids, mzs, outCols):
    with open(outTsv, 'w') as f:
            stemp = '\t'.join([str(x) for x in sids])
            print(f"m/z\t{stemp}", file = f)
            for i_mz, mz in enumerate(mzs):
                stemp = f"{mz}"
                for i_col, col in enumerate(outCols):
                    if i_mz < len(col): 
                        stemp += f"\t{col[i_mz]}"
                    else:
                        stemp += ""
                print(stemp, file = f)

    
def mzFiltered(mzMLIn, spectrumIndices, outTsv, mzs, tol, filterMS2 = True):
    print("Starting mzFiltered output...")
    tol = float(tol)
    ode = OnDiscMSExperiment()
    ode.openFile(mzMLIn)
    sids = readTxt(spectrumIndices)
    mzs = readTxt(mzs)
    outCols = []
    # for sid in tqdm(sids):
    #     outCol = []
    #     sid = int(sid)
    #     spec = ode.getSpectrum(sid)
    #     s_mzs, s_ints = spec.get_peaks()
    #     for rmz in mzs:
    #         rmz = float(rmz)
    #         hitIdxs = np.where(np.abs(rmz - s_mzs) < tol)[0]
    #         hits = sorted(zip(s_mzs[hitIdxs], s_ints[hitIdxs]), key = lambda x : x[1], reverse = True)
    #         if len(hits) == 0:
    #             outCol.append("")
    #         else:
    #             hmz, hintensity = hits[0]
    #             outCol.append(hintensity)
    for sid in tqdm(sids):
        outCol = getOutCol(sid, ode, mzs, mzMLIn, tol, filterMS2=filterMS2)
        outCols.append(outCol)
    # with open(outTsv, 'w') as f:
    #     stemp = '\t'.join([str(x) for x in sids])
    #     print(f"m/z\t{stemp}", file = f)
    #     for i_mz, mz in enumerate(mzs):
    #         stemp = f"{mz}"
    #         for i_col, col in enumerate(outCols):
    #             stemp += f"\t{col[i_mz]}"
    #         print(stemp, file = f)
    writeOutTsv(outTsv, sids, mzs, outCols)
    print("Done")


    

def multiMzFiltered(inTsv, mzs, outDirectory, tol, filterMS2 = True):
    print("Starting multiMzFiltered output...")
    os.system(f"mkdir -p {outDirectory}")
    tol = float(tol)
    mzs = readTxt(mzs)
    inFile = open(inTsv, 'r')
    for line in inFile:
        line = line.strip().split('\t')
        mzMLIn = line[0]
        sids = [int(x) for x in line[1 : ]]
        ode = OnDiscMSExperiment()
        ode.openFile(mzMLIn)
        outCols = []
        for sid in sids:
            outCol = getOutCol(sid, ode, mzs, mzMLIn, tol, filterMS2=filterMS2)
            outCols.append(outCol)
        mzmlPref = ".".join(os.path.basename(mzMLIn).split('.')[0 : -1])
        outTsv = os.path.join(outDirectory, f"{mzmlPref}.tsv")
        writeOutTsv(outTsv, sids, mzs, outCols)
    inFile.close()


    
def main():
    args = docopt(__doc__, version='pzMZML 0.1')
    if args["tsvs"]:
        singleFiles(args["<mzMLIn>"], args["<spectrumIndices>"], args["<outDirectory>"], filterMS2= not args['--noMS2Filter'])
    if args["mzFiltered"]:
        mzFiltered(args["<mzMLIn>"], args["<spectrumIndices>"], args["<outTsv>"], args["<mzs>"], args["--tolerance"], filterMS2= not args['--noMS2Filter'])
    if args["multiMzFiltered"]:
        multiMzFiltered(args["<inTsv>"], args["<mzs>"], args["<outDirectory>"], args["--tolerance"], filterMS2= not args['--noMS2Filter'])
    
################################################################################

if __name__ == '__main__':
    main()
