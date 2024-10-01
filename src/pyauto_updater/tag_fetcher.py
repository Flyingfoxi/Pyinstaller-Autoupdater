# -*- coding: utf-8 -*-
"""
filename:   tag_fetcher.py
project:    Pyinstaller-Autoupdater
"""

import os
import tempfile

import requests as _requests

from .exceptions import InvalidRepository as _InvalidRepo

tag_form = dict[str: str]


def get_latest_release(owner: str, repo: str) -> tag_form | None:
    url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
    with _requests.get(url) as response:
        if response.status_code == 200:
            try:
                release = response.json()
            except _requests.exceptions.JSONDecodeError as ex:
                raise ValueError("unable to parse response") from ex

        else:
            raise _InvalidRepo(owner, repo)
    return release


def check_for_update(tag1, tag2):
    def parse_tag(tag):
        return list(map(int, tag.strip('v').split('.')))

    version1 = parse_tag(tag1)
    version2 = parse_tag(tag2)

    tag_length = max(len(version1), len(version2))
    version1.extend([0] * (tag_length - len(version1)))
    version2.extend([0] * (tag_length - len(version2)))

    for v1, v2 in zip(version1, version2):
        if v1 > v2:
            return True
        elif v1 < v2:
            return False

    # if they are the same
    return False


def download_zip(url, file):
    temp_zip = os.path.join(tempfile.gettempdir(), file)

    with _requests.get(url, stream=True) as response:
        response.raise_for_status()

        with open(temp_zip, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):  # Download in chunks
                if chunk:
                    f.write(chunk)

    return temp_zip
