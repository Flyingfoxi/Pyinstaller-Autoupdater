# Pyinstaller-Autoupdater
Makes Pyinstaller Application easier to be distributed due to automatic updates with a github repo (Release Binarys)

# Example implementation

```python
from pyauto-updater import Updater

# latest version is automaticly checked
updater = Updater(
  current_version = "v0.1"
  owner = "username",
  repository = "repo"
)

if updater.update_available:
  # your interface for asking the user to update
  updater.do_update()
```
  
## This Project is still in Development, so be free to contribute
- Issues or Discussions are a good spot to look.
