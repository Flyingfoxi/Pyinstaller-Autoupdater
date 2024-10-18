# -*- coding: utf-8 -*-
"""
filename:   script_worker.py
project:    Pyinstaller-Autoupdater
"""
import logging
import os
import platform
import subprocess
import tempfile

IS_WINDOWS = (platform.system() == "Windows")

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
echo Unzipping "%zip%"
tar -xf "%zip%" -C "%dest%"
del "%zip%"
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
log_file="{log}"
tmp_dir="/tmp/backup_dir_$(date +%s)"  # Unique tmp dir based on timestamp

exec > >(tee -a $log_file) 2>&1

log() {{
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}}

error_exit() {{
    log "Error: $1"
    
    if [ -d "$tmp_dir" ]; then
        log "Restoring directory from $tmp_dir to $dir"
        mv "$tmp_dir"/* "$dir"/ || log "Failed to restore directory from $tmp_dir"
    fi
    exit 1
}}

# Check if directory exists and move to tmp dir
if [ -d "$dir" ]; then
    mv "$dir" "$tmp_dir" || error_exit "Failed to move $dir to $tmp_dir"
    log "Moved $dir to $tmp_dir"
else
    log "Directory not found: $dir"
fi

# Create destination directory
mkdir -p "$dest" || error_exit "Failed to create directory: $dest"
log "Created destination directory: $dest"

# Unzip file
log "Unzipping $zip ..."
unzip "$zip" -d "$dest" || error_exit "Failed to unzip $zip"
rm "$zip" || error_exit "Failed to delete zip file: $zip"
log "Successfully finished"

# Cleanup: remove tmp_dir if everything is successful
if [ -d "$tmp_dir" ]; then
    rm -rf "$tmp_dir" || log "Failed to delete temporary backup directory: $tmp_dir"
    log "Deleted temporary backup directory: $tmp_dir"
fi

exit 0

'''


def create_script(executable, zip_location, destination, log_file):
    _logger = logging.getLogger("py-autoupdater")
    _logger.debug(msg=("Using Batch Script" if IS_WINDOWS else "Using Bash Script"))
    script = (script_windows if IS_WINDOWS else script_unix)
    script = script.format(
            dir=os.path.abspath(os.path.dirname(executable)),
            zip=zip_location,
            destination=destination,
            log=log_file
    )

    script_location = os.path.join(tempfile.gettempdir(), f"update-script.{"bat" if IS_WINDOWS else "sh"}")
    _logger.info(msg=f"Saved Script to {script_location}")

    with open(script_location, "w") as f:
        f.write(script)

    if IS_WINDOWS:
        subprocess.Popen(["cmd", "/c", script_location])

    else:
        subprocess.run(["chmod", "777", script_location])
        subprocess.Popen(["bash", script_location])
    _logger.debug(msg="script started")
