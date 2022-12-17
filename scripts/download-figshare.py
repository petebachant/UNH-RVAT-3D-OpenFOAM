#!/usr/bin/env python
"""Download case results from Figshare.

The `wget` Python module can be installed via

    pip install wget
"""

from __future__ import division, print_function
import requests
import tarfile
import json
import os
import re
import wget
import sys


article = "2885308"
BASE_URL = "https://api.figshare.com/v2/{endpoint}"


def get_article_details():
    endpoint = "articles/{}".format(article)
    resp = requests.get(BASE_URL.format(endpoint=endpoint))
    return json.loads(resp.content.decode())


def get_uploaded_files():
    """Return a list of dictionaries describing each file."""
    return get_article_details()["files"]


def get_uploaded_filenames():
    flist = get_uploaded_files()
    return [f["name"] for f in flist]


def get_remote_url(filename):
    """Return remote URL for downloading file."""
    files = get_uploaded_files()
    base = "https://ndownloader.figshare.com/files/{id}"
    remote_urls = {f["name"]: base.format(id=f["id"]) for f in files}
    return remote_urls[filename]


def download_file(filename):
    """Download remote file using the `wget` Python module."""
    url = get_remote_url(filename)
    wget.download(url, out=filename)


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


def test_download_file(fname="0.02.gz"):
    download_file(fname)
    os.remove(fname)


if __name__ == "__main__":
    # Script should be run from case root directory
    if os.path.split(os.getcwd())[-1] == "scripts":
        print("Changing working directory to case root directory")
        os.chdir("../")

    # Create list of local files and directories
    local_items = os.listdir("./")

    # Create list of files on Figshare
    remote_files = get_uploaded_filenames()

    # If filename(s) are passed to script, download those
    if len(sys.argv) > 1:
        flist = sys.argv[1:]
    else:
        flist == remote_files

    for f in flist:
        # File name could end with ".gz"
        if not f in local_items and not f[:-3] in local_items:
            print("Downloading {}".format(f))
            download_file(f)
            if f.endswith(".gz"):
                print("Uncompressing {}".format(f))
                uncompress_file(f)
                print("Deleting local copy of {}".format(f))
                os.remove(f)
        else:
            print("{} already exists".format(f))
