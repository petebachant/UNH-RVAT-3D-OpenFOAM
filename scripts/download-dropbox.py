#!/usr/bin/env python
"""Download case results from Dropbox.

Needs an access token to do so. The case will need to have the same name as the
top-level directory. Note that the script should be run from the top-level
directory, not the scripts directory.

This script should be run with Python 2.7. With Anaconda, first create a
conda env:
```
conda create -n dropbox python=2.7
source activate dropbox
pip install dropbox
```

Then run the script (from the top-level case directory):
```
source activate dropbox # Only necessary if a new terminal
python scripts/download.py
```
"""
from __future__ import division, print_function
from dropbox.client import DropboxClient
from dropbox.rest import ErrorResponse
import subprocess
import tarfile
import json
import os
import re

def download_file(client, filename, directory="/"):
    out = open(filename, "wb")
    with client.get_file(os.path.join(directory, filename)) as f:
        out.write(f.read())
    out.close()

def get_token():
    rcpath = os.path.join(os.path.expanduser("~"),
                          "Google Drive",
                          "Settings and Presets",
                          ".dropboxrc")
    with open(rcpath) as f:
        token = json.load(f)["token"]
    return token

def get_dropbox_contents(client, dbdir):
    try:
        folder_metadata = client.metadata(dbdir)
        dbcontents = folder_metadata["contents"]
    except ErrorResponse:
        dbcontents = []
    return dbcontents

def get_dropbox_filelist(client, dbdir):
    """Returns list of tuples of filenames and sizes."""
    dbcontents = get_dropbox_contents(client, dbdir)
    dbfilelist = []
    for f in dbcontents:
        dbfilelist.append(str(f["path"].split("/")[-1]))
    return sorted(dbfilelist)

def uncompress_file(filename):
    with tarfile.open(filename, "r:gz") as tf:
        def is_within_directory(directory, target):
            
            abs_directory = os.path.abspath(directory)
            abs_target = os.path.abspath(target)
        
            prefix = os.path.commonprefix([abs_directory, abs_target])
            
            return prefix == abs_directory
        
        def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
        
            for member in tar.getmembers():
                member_path = os.path.join(path, member.name)
                if not is_within_directory(path, member_path):
                    raise Exception("Attempted Path Traversal in Tar File")
        
            tar.extractall(path, members, numeric_owner=numeric_owner) 
            
        
        safe_extract(tf)

if __name__ == "__main__":
    # Name the case the subfolder
    casename = os.path.split(os.getcwd())[-1]
    # Path for files on Dropbox
    dbdir = os.path.join("OpenFOAM", "solvedCases", casename)

    # Create Dropbox client
    token = get_token()
    client = DropboxClient(token)

    # Create list of local files and directories
    local_items = os.listdir("./")

    # Create list of files on Dropbox
    db_files = get_dropbox_filelist(client, dbdir)

    for f in db_files:
        if not f in local_items and not f[:-3] in local_items:
            print("Downloading {}".format(f))
            download_file(client, f, directory=dbdir)
            if f[-3:] == ".gz":
                print("Uncompressing {}".format(f))
                uncompress_file(f)
                print("Deleting local copy of {}".format(f))
                os.remove(f)
        else:
            print("{} already exists".format(f))
