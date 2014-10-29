#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: pete

This script will download case results from Dropbox, and needs an access
token to do so. The case will need to have the same name as the top-level
directory.
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
    with open(os.path.join(os.path.expanduser("~"), ".dropboxrc")) as f:
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
    return dbfilelist
        
def uncompress_file(filename):
    with tarfile.open(filename, "r:gz") as tf:
        tf.extractall()
        
if __name__ == "__main__":
    # Name the case the subfolder where this script is located
    casename = os.path.dirname(os.path.realpath(__file__)).split("/")[-1]
    # Path for files on Dropbox
    dbdir = os.path.join("/OpenFOAM/solvedCases", casename)

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
            if f[:-3] == ".gz":
                print("Uncompressing {}".format(f))
                uncompress_file(f)
                print("Deleting local copy of {}".format(f))
                os.remove(f)
        else:
            print("{} already exists".format(f))

