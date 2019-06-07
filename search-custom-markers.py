#! /usr/bin/env python 

import os, sys
import glob 
import argparse
import subprocess 
import pandas as pd 
from Bio import SearchIO

# Arguments and Setup
parser = argparse.ArgumentParser(description = "Search custom direcotory of HMMs")
parser.add_argument('--genome_dir', metavar='GENOMEDIR', help='Directory where genomes to be screened are held')
parser.add_argument('--markers_dir', metavar='MARKERDIR', help="Direcotory where markers are held")
parser.add_argument('--output', metavar='OUTFILE', default="custom-metabolic-markers-results.txt", help="Name of output file of results")

args = parser.parse_args()
GENOMEDIR = args.genome_dir
MARKERDIR = args.markers_dir
OUTFILE = args.output

os.mkdir("out")
os.mkdir("results")
genomes=glob.glob(os.path.join(GENOMEDIR, '*.faa'))
markers=glob.glob(os.path.join(MARKERDIR, "*.hmm"))
FNULL = open(os.devnull, 'w')

# Run HMMs
for genome in genomes: 
    name=os.path.basename(genome).replace(".faa", "").strip().splitlines()[0]
    dir=name
    os.mkdir("out/"+dir)
    for marker in markers:
        prot=os.path.basename(marker).replace(".hmm", "").strip().splitlines()[0]
        outname= "out/"+dir+"/"+name + "-" + prot + ".out"
        cmd = ["hmmsearch","--cut_tc","--tblout="+outname, marker, genome]
        subprocess.call(cmd, stdout=FNULL)
        print("Running HMMsearch on " + name + " and " + prot + " marker")

# Parse HMM file to results matrix/dataframe
print("Parsing all results...")
all_dicts={}
result_dirs = os.walk("out/")
for path, dirs, files in result_dirs:
    genome_dict={}
    for file in files:
        genome = file.split("-")[0]
        prot = file.replace(".out", "").split("-")[1]
        result = "out/"+genome+"/"+file
        with open(result, "rU") as input:
            for qresult in SearchIO.parse(input, "hmmer3-tab"):
                hits = qresult.hits
                num_hits = len(hits)
                genome_dict[prot] = num_hits
                all_dicts[os.path.basename(file).split("-")[0]]=genome_dict
df=pd.DataFrame.from_dict(all_dicts, orient="index", dtype=None)

# Reformat dataframe in order of marker function, find markers in none of the genomes and input NaN for all
all_cols=[]
absent_cols=[]
existing_markers = df.columns
for marker in markers:
    prot=os.path.basename(marker).replace(".hmm", "")
    if prot not in existing_markers:
        all_cols.append(prot)
for col in existing_markers:
    all_cols.append(col)
df_all=df.reindex(columns=all_cols)
df_all.fillna(0, inplace=True)
df_all.to_csv(OUTFILE)