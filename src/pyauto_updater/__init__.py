# -*- coding: utf-8 -*-
"""
filename:   __init__.py
project:    Pyinstaller-Autoupdater
"""

import os
import platform
import sys


from . import (
    updater,
    tag_fetcher,
    script_worker,
    exceptions
)

from .__version__ import *


def find_executable():
    if getattr(sys, 'frozen', False):
        executable = sys.executable
    else:
        executable = os.path.abspath(__file__)
    return executable


class Updater:
    def __init__(self,
                 current_version: str,
                 owner: str,
                 repository: str,
                 assets_name: str = "dist-{}",
                 executable: str = find_executable(),
                 destination: str = os.path.dirname(find_executable()),
                 check_now: bool = True
                 ):
        self.update_available = False
        self.newest_tag = None

        self.version = current_version
        self.owner = owner
        self.repo = repository
        self.assets_name = assets_name.format(platform.system()) + ".zip"
        self.executable = executable
        self.destination = destination

        if check_now:
            self._check_for_update()

    def _check_for_update(self):
        self.newest_tag = tag_fetcher.get_latest_release(self.owner, self.repo)
        self.update_available = tag_fetcher.check_for_update(self.newest_tag["tag_name"], self.version)
        return self.update_available

    def do_update(self, enforce=False):
        assert self.newest_tag is not None

        if enforce or self.update_available:
            assets = {i["name"]: i for i in self.newest_tag["assets"]}

            if self.assets_name not in assets:
                raise ValueError(f"\"{self.repo}\" does not have a release for {platform.system()}")

            url = assets[self.assets_name]["browser_download_url"]
            name = self.assets_name

            file = tag_fetcher.download_zip(url, name)
            script_worker.create_script(self.executable, file, self.destination)

            # exiting to let the subprocess.Popen to delete the executable
            sys.exit(0)
