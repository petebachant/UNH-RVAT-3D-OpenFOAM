#!/usr/bin/env python
"""This script uploads simulation results to Figshare.

It should be run with a `.figsharerc` file in the user"s home directory.
`article` must be an existing article on Figshare created for this dataset.

Note that no error checking is done, so if a file upload is incomplete, the
only way to know is to inspect the article on the Figshare web interface.
"""

from __future__ import division, print_function
import requests
import os
import json
import tarfile
import re


article = "2885308"


def load_credentials():
    with open(os.path.join(os.path.expanduser("~"), ".figsharerc")) as f:
        cred = json.load(f)
    return cred


def get_article_details():
    BASE_URL = "https://api.figshare.com/v2/{endpoint}"
    TOKEN = load_credentials()["personal_token"]
    HEADERS = {"Authorization": "token " + TOKEN}
    endpoint = "account/articles/{}".format(article)
    resp = requests.get(BASE_URL.format(endpoint=endpoint), headers=HEADERS)
    return json.loads(resp.content.decode())


def get_uploaded_files():
    """Return a list of dictionaries describing each file."""
    return get_article_details()["files"]


def get_uploaded_filenames():
    flist = get_uploaded_files()
    return [f["name"] for f in flist]


def make_local_items_list():
    """Create list of local items to compress and upload."""
    local_items = os.listdir("./")
    local_items_list = []
    for f in local_items:
        if re.match("^\d+$", f) or re.match("^\d+\.\d+$", f) or \
                f in ["constant", "postProcessing", "log.pimpleDyMFoam"]:
            if os.path.isdir(f) or f == "log.pimpleDyMFoam":
                local_items_list.append(f)
    local_items_list.remove("0")
    return sorted(local_items_list)


def get_remote_urls(write=True):
    files = get_uploaded_files()
    base = "https://ndownloader.figshare.com/files/{id}"
    remote_urls = {f["name"]: base.format(id=f["id"]) for f in files}
    if write:
        with open("constant/urls.json", "w") as f:
            json.dump(remote_urls, f, indent=4)
    return remote_urls


def upload_file(fpath_local, fpath_remote=None, client=None, oauth=None,
                verbose=True):
    """Upload a file using the Figshare v2 API."""
    if fpath_remote is None:
        fpath_remote = fpath_local

    # Below from Figshare API v2 documentation example
    BASE_URL = "https://api.figshare.com/v2/{endpoint}"
    TOKEN = load_credentials()["personal_token"]
    HEADERS = {"Authorization": "token " + TOKEN}
    article_id = str(article)

    # Get file info
    with open(fpath_local, "rb") as fin:
        fin.seek(0, 2)  # Go to end of file
        size = fin.tell()
    data = json.dumps({"name": fpath_remote, "size": size})

    # Initiate upload
    endpoint = "account/articles/{}/files".format(article_id)
    resp = requests.post(BASE_URL.format(endpoint=endpoint),
                         headers=HEADERS, data=data)

    file_id = json.loads(resp.content.decode())["location"].rsplit("/", 1)[1]

    # Get upload/parts info
    endpoint = "account/articles/{}/files/{}".format(article_id, file_id)
    resp = requests.get(BASE_URL.format(endpoint=endpoint), headers=HEADERS)

    url = "{upload_url}".format(**json.loads(resp.content.decode()))
    parts = json.loads(requests.get(url).content.decode())["parts"]

    # Upload parts
    with open(fpath_local, "rb") as fin:
        for part in parts:
            size = part["endOffset"] - part["startOffset"] + 1
            address = "{}/{}".format(url, part["partNo"])
            requests.put(address, data=fin.read(size))

    # Mark file upload as completed
    requests.post(BASE_URL.format(endpoint=endpoint), headers=HEADERS)


def upload_all(overwrite=False):
    """Upload all files to Figshare."""
    # Create list of local items
    local_items = make_local_items_list()
    local_files = [d + ".gz" for d in local_items]

    # Create list of files on Figshare
    uploaded_files = get_uploaded_filenames()

    # Iterate through local items, compress directories if necessary, and
    # upload if not already present
    for d in local_items:
        if d != "log.pimpleDyMFoam":
            f = d + ".gz"
        else:
            f = d
        if not f in uploaded_files:
            print("Compressing {}".format(d))
            if f != "constant.gz" and f != "postProcessing.gz" and f != \
                    "log.pimpleDyMFoam":
                compress_dir(d, files=["U", "p", "k", "nut", "uniform",
                                       "polyMesh"])
            elif f == "log.pimpleDyMFoam":
                pass
            else:
                compress_dir(d)
            print("Uploading {}".format(f))
            upload_file(f)
            make_article_public()
            if f != "log.pimpleDyMFoam":
                print("Deleting local copy of {}".format(f))
                os.remove(f)
        else:
            print("{} already uploaded".format(f))


def test_upload_file():
    with open("test.txt", "w") as f:
        f.write("This is a test.")
    upload_file("test.txt")
    uploaded_files = get_uploaded_filenames()
    print(uploaded_files)
    assert "test.txt" in uploaded_files
    os.remove("test.txt")


def test_upload_large_file(fpath="0.02.gz"):
    """Attempt to upload a large file."""
    remote_name = make_remote_name(fpath)
    upload_file(fpath, remote_name)
    uploaded_files = get_uploaded_filenames()
    print(uploaded_files)
    assert fpath in uploaded_files


def make_article_public():
    """Make the article public on Figshare. Must be done to avoid storage
    limits, and plus, this is the point.
    """
    # Below from Figshare API v2 documentation example
    BASE_URL = "https://api.figshare.com/v2/{endpoint}"
    TOKEN = load_credentials()["personal_token"]
    HEADERS = {"Authorization": "token " + TOKEN}
    article_id = str(article)
    # Publish
    endpoint = "account/articles/{}/publish".format(article_id)
    resp = requests.post(BASE_URL.format(endpoint=endpoint), headers=HEADERS)


def compress_dir(directory, files="all"):
    """Compress a directory to a tarfile."""
    with tarfile.open(directory+".gz", "w:gz") as tf:
        if files == "all":
            files = os.listdir(directory)
        for f in files:
            print("Adding {} to {}".format(f, directory + ".gz"))
            tf.add(os.path.join(directory, f))


if __name__ == "__main__":
    if os.path.split(os.getcwd())[-1] == "scripts":
        print("Changing working directory to case root directory")
        os.chdir("../")

    upload_all(overwrite=False)
