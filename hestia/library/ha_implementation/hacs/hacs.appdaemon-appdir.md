# AppDir Structure

So far, we have assumed that all apps and their configuration files are placed in a single directory. This works fine for simple setups but as the number of apps grows, it can be useful to organize them into subdirectories. AppDaemon will automatically search all subdirectories of the apps directory for apps and configuration files. This means that you can have a directory structure like this:

```
conf/apps
├── app1
│   ├── app1.py
│   └── app1.yaml
├── app2
│   ├── app2.py
│   └── app2.yaml
├── common
│   ├── my_globals.py
│   └── utils.py
└── some
    └── deep
        └── path
            ├── app3.py
            └── app3.yaml
```

In this example, AppDaemon will find all the apps defined in `app1.yaml`, `app2.yaml`, and even `app3.yaml`, despite it being deep in a subdirectory. Each of those files would define apps using module: app1 or module: app2 etc. to refer to their respective python modules.

Additionally, apps in `app1.py`, `app2.py`, and `app3.py` can import things directly from `my_globals.py` and `utils.py` like this:

```py
# app1/app1.py

from appdaemon.adapi import ADAPI

from my_globals import MY_GLOBAL_VAR
from utils import my_util_function

class MyApp(ADAPI):
    def initialize(self):
        ... # app code would go here
```

> Note: There are no relative paths here. AppDaemon handles adding all the relevant subdirectories to the import path, which allows them to be directly imported, as if the files were next to each other. Furthermore, AppDaemon understands that app1.py depends on both my_globals.py and utils.py, so if either of those files change, AppDaemon will reload app1.py automatically.

