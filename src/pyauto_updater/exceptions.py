# -*- coding: utf-8 -*-
"""
filename:   exceptions.py
project:    Pyinstaller-Autoupdater
"""


class InvalidRepository(ValueError):
    """ Repository not found """

    def __init__(self, owner, repo):
        message = f"The user \"{owner}\" doesn't have a repository named \"{repo}\""
        super().__init__(message)


class Invalid(ValueError):
    ...
