# -*- coding: utf-8 -*-
"""
filename:   __init__.py
project:    Pyinstaller-Autoupdater
"""

import os
import platform
import sys
import logging
import time

from . import (
    tag_fetcher,
    script_worker,
    exceptions,
)

__all__ = ["Updater"]


class Logger(logging.Logger):
    file_encoding: str = "utf-8"
    file_mode: str = "a+"
    file_delay: bool = False

    def __init__(self, name, destination, level=logging.WARNING):
        super().__init__(name, level)

        file_handler = logging.FileHandler(
                destination,
                self.file_mode,
                self.file_encoding,
                self.file_delay
        )

        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
        self.addHandler(file_handler)


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
                 log_file: str = os.path.join(os.path.dirname(find_executable()), "logs", "py-autoupdater" + str(time.time()) + ".log"),
                 executable: str = find_executable(),
                 destination: str = os.path.dirname(find_executable()),
                 check_now: bool = True
                 ):

        if not os.path.exists(os.path.dirname(log_file)):
            os.mkdir(os.path.dirname(log_file))
        with open(log_file, "w") as f:
            f.write("")

        self._logger = Logger(f"py-autoupdater", log_file, level=logging.DEBUG)
        self._logger.info(msg=f"Init for {owner}/{repository}")
        self._logger.info(msg=f"Current Version: {current_version}")

        self.update_available = False
        self.newest_tag = None

        self.version = current_version
        self.owner = owner
        self.repo = repository
        self.assets_name = assets_name.format(platform.system()) + ".zip"
        self.executable = executable
        self.destination = destination
        self.log_file = log_file

        if check_now:
            self._check_for_update()

    def _check_for_update(self):
        self.newest_tag = tag_fetcher.get_latest_release(self.owner, self.repo)
        self.update_available = tag_fetcher.check_for_update(self.newest_tag["tag_name"], self.version)
        self._logger.info(msg=f"Newest Tag: {self.newest_tag["tag_name"]}, Update Available: {self.update_available}")
        return self.update_available

    def do_update(self, force=False):
        assert self.newest_tag is not None

        if force:
            self._logger.info("Process Forced Update ...")

        if force or self.update_available:
            assets = {i["name"]: i for i in self.newest_tag["assets"]}

            if self.assets_name not in assets:
                raise ValueError(f"\"{self.repo}\" does not have a release for {platform.system()}")

            url = assets[self.assets_name]["browser_download_url"]
            self._logger.info(f"Found URL for Download: {url}")
            name = self.assets_name

            file = tag_fetcher.download_zip(url, name)
            self._logger.info(f"Saved ZIP file to {file}")
            script_worker.create_script(self.executable, file, self.destination, self.log_file)

            self._logger.info(f"Saved Script, exiting ...")
            # exiting to let the subprocess.Popen to delete the executable
            sys.exit(0)
