# 💊 Extract DailyMed SPL

Extracting the indication from the SPLs (Structured Product Labeling) that are coming from DailyMed dataset.

## Clone

This project has a `git submodule` where the data are stored on a hugging face git repository. This module uses git large file storage.
Use the following to automatically extract and set up the submodule when cloning the repository

```
git lfs install
```
```
git clone --recurse-submodules https://github.com/MaastrichtU-IDS/extract-dailymed-spl
```


Otherwise, you can initialize, fetch and checkout the nested submodule with the following command

```
git submodule update --init --recursive
```


## Install

Create and activate virtual env

```bash
python -m venv .venv
source .venv/bin/activate
```

Install

```bash
pip install -e .
```

## Run

Parameters 
```
usage: Dailymed Parser [-h] [-w WORKING_DIR] [-d DOWNLOAD] [-f] [-a DATE] [-s FILES] [-e EXTRACT] [-p PROCESS]

Downloads and parses Dailymed product labels

options:
  -h, --help            show this help message and exit
  -w WORKING_DIR, --working_dir WORKING_DIR
                        Directory to download files into
  -d DOWNLOAD, --download DOWNLOAD
                        Download content, if it hasn't already been downloaded.
  -f, --force           Replace files, even if they were previously downloaded
  -a DATE, --date DATE  Use data from specified date in format of YYYY-MM-DD
  -s FILES, --files FILES
                        Specify a comma-separated list of the files to download/process. options: all|prescription|otc
  -e EXTRACT, --extract EXTRACT
                        Extract XML files from download files
  -p PROCESS, --process PROCESS
                        Extract XML files from download files
```

```bash
python src/dm_parser.py
```
