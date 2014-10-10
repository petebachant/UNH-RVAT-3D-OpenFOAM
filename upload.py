# -*- coding: utf-8 -*-
"""
Created on Thu Oct  9 20:17:56 2014

@author: pete

This script will upload case results to Dropbox, ans needs an access
token to do so.
"""
from __future__ import division, print_function
from dropbox.client import DropboxClient
from dropbox.rest import ErrorResponse
import json
import os
import re

def upload_file(filename):    
    with open(filename, "rb") as f:
        response = client.put_file(os.path.join(dbdir, filename), f, 
                                   overwrite=True)
    print(response)

def get_token():
    with open(os.path.join(os.path.expanduser("~"), ".dropboxrc")) as f:
        token = json.load(f)["token"]
    return token

def get_local_file_list():
    """Create list of local directories to compress and upload."""
    local_items = os.listdir("./")
    items_to_upload = []
    for f in local_items:
        if re.match("^\d+", f) or re.match("^\d+\.\d+", f) or \
                f in ["constant", "postProcessing"]:
            items_to_upload.append(f)

def get_dropbox_contents(client):
    try:
        folder_metadata = client.metadata(dbdir)
        dbcontents = folder_metadata["contents"]
    except ErrorResponse, e:
        dbcontents = []
    return dbcontents
        
uploaded_files = []
for f in dbcontents:
    print(f["size"])
    uploaded_files.append(str(f["path"].split("/")[-1]))
    
print(uploaded_files)
        
if __name__ == "__main__":
    # Call the case the subfolder where this script is located
    casename = os.path.dirname(os.path.realpath(__file__)).split("/")[-1]
    # Path for files on Dropbox
    dbdir = os.path.join("/OpenFOAM/solvedCases", casename)

    # Create Dropbox client    
    token = get_token()    
    client = DropboxClient(token)