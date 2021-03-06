#! /usr/bin/env python3

import github
import os
import shutil
import subprocess
import tempfile
import urllib

g = github.Github()  # read-only, no token needed
tag_name = os.environ["GITHUB_TAG"]
tag_prefix = "refs/tags/"
if tag_name.startswith(tag_prefix):
    tag_name = tag_name[len(tag_prefix):]

repo = g.get_repo("xyb/rocksdb-py")

releases = list(repo.get_releases())
for release in releases:
    if release.tag_name == tag_name:
        break
else:
    raise RuntimeError("no release for tag " + repr(tag_name))

asset_names = [asset.name for asset in release.get_assets()]
asset_files = []

tempdir = tempfile.mkdtemp()
for asset_name in asset_names:
    urlbase = "https://github.com/xyb/rocksdb-py/releases/download/{}/{}"
    url = urlbase.format(tag_name, asset_name)
    filepath = os.path.join(tempdir, asset_name)
    asset_files.append(filepath)
    with urllib.request.urlopen(url) as request, open(filepath, "wb") as f:
        print("Downloading " + asset_name)
        shutil.copyfileobj(request, f)

print("Uploading to PyPI with twine...")
# Credentials are in the environment, TWINE_USERNAME and TWINE_PASSWORD.
twine_cmd = ["twine", "upload"] + asset_files
subprocess.run(twine_cmd, check=True)

print("Success!")
