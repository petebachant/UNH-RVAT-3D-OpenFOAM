#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Thu Oct  9 20:17:56 2014

@author: pete

This script will upload case results to Dropbox, and needs an access
token to do so.
"""
from __future__ import division, print_function
from dropbox.client import DropboxClient
from dropbox.rest import ErrorResponse
import subprocess
import tarfile
import json
import os
import re

def upload_file(client, filename, dbdir):
    size = os.path.getsize(filename)
    with open(filename, "rb") as f:
        uploader = client.get_chunked_uploader(f, size)
        while uploader.offset < size:
            try:
                upload = uploader.upload_chunked()
            except ErrorResponse as e:
                print(e)
    uploader.finish(os.path.join(dbdir, filename))

def get_token():
    with open(os.path.join(os.path.expanduser("~"), ".dropboxrc")) as f:
        token = json.load(f)["token"]
    return token

def get_local_dir_list():
    """Create list of local directories to compress and upload."""
    local_items = os.listdir("./")
    local_dir_list = []
    for f in local_items:
        if re.match("^\d+$", f) or re.match("^\d+\.\d+$", f) or \
                f in ["constant", "postProcessing"]:
            if os.path.isdir(f):
                local_dir_list.append(f)
    return sorted(local_dir_list)

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
        
def compress_dir(directory, files=["U", "p", "k", "uniform", "polyMesh"]):
    with tarfile.open(directory+".gz", "w:gz") as tf:
        for f in files:
            print("Adding {} to {}".format(f, directory + ".gz"))
            tf.add(os.path.join(directory, f))
        
if __name__ == "__main__":
    # Name the case the subfolder where this script is located
    casename = os.path.dirname(os.path.realpath(__file__)).split("/")[-1]
    # Path for files on Dropbox
    dbdir = os.path.join("/OpenFOAM/solvedCases", casename)

    # Create Dropbox client    
    token = get_token()    
    client = DropboxClient(token)
    
    # Create list of local directories
    local_dirs = get_local_dir_list()
    local_files = [d + ".gz" for d in local_dirs]
    
    # Create list of files on Dropbox
    db_files = get_dropbox_filelist(client, dbdir)
    
    for d in local_dirs:
        f = d + ".gz"
        if not f in db_files:
            print("Compressing {}".format(d))
            compress_dir(d)
            print("Uploading {}".format(f))
            upload_file(client, f, dbdir)
            print("Deleting local copy of {}".format(f))
            os.remove(f)
        else:
            print("{} already uploaded".format(f))
