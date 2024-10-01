# -*- coding: utf-8 -*-
"""
filename:   script_worker.py
project:    Pyinstaller-Autoupdater
"""

import os
import platform
import subprocess
import tempfile

IS_WINDOWS = (platform.system() == "windows")

script_windows = '''
@echo off
setlocal

timeout /t 3 /nobreak

set "dir={dir}"
set "zip={zip}"
set "dest={destination}"

if exist "%dir%" (
    rmdir /s /q "%dir%"
    echo Deleted directory: "%dir%"
) else (
    echo Directory not found: "%dir%"
)

mkdir "%dest%"
echo Unzipping "$zip"
tar -xf "$zip" -C "$dest"
del "$zip"
echo Sucessfully finished

endlocal
exit
'''

script_unix = '''
#!/usr/bin/bash

sleep 3

dir="{dir}"
zip="{zip}"
dest="{destination}"

if [ -d "$dir" ]; then
    rm -r "$dir"
    echo "Deleted directory: $dir"
else
    echo "Directory not found: $dir"
fi

mkdir -p $dest
echo "Unzipping $zip ..."
unzip $zip -d $dest
rm $zip
echo "Successfully finished"
exit
'''


def create_script(executable, zip_location, destination):
    script = (script_windows if IS_WINDOWS else script_unix)
    script = script.format(
            dir=os.path.abspath(os.path.dirname(executable)),
            zip=zip_location,
            destination=destination
    )

    script_location = os.path.join(tempfile.gettempdir(), f"update-script-for-agenda.{"bat" if IS_WINDOWS else "sh"}")

    with open(script_location, "w") as f:
        f.write(script)

    if IS_WINDOWS:
        subprocess.Popen(["cmd", "/c", script_location])

    else:
        subprocess.run(["chmod", "777", script_location])
        subprocess.Popen(["bash", script_location])
