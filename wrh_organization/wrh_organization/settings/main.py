import sys
import traceback

from .base import *

########## Load external config ##########
SETTINGS_PATH = Path(__file__).parent.absolute()
try:
    from .external import *
except (ImportError, FileNotFoundError):
    try:
        from .local import *
    except (ImportError, FileNotFoundError):
        print(f'Could not detect a setting file. you have this options\n'
              f'1- put a local setting file in {SETTINGS_PATH}/local.py (for local development)\n'
              f'2- put an external setting file in {EXTERNAL_CONFIG_PATH} (for remote deployment)\n'
              f'3- make a setting file in {SETTINGS_PATH} path and pass that '
              f'as --settings option\n')
        sys.exit(1)
except Exception:
    print('!!!PLEASE CHECK!!! Invalid external setting file or json: [{}].'.format(EXTERNAL_CONFIG_PATH))
    traceback.print_exc()
    sys.exit(2)

#############################################
