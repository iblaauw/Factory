import inspect
import os

def get_caller_dict():
     return inspect.stack()[2][0].f_globals

def get_num_params(callable_val):
    sig = inspect.signature(callable_val)
    return len(sig.parameters)

def modify_time(path):
    if path is None:
        return -1
    if not os.path.isfile(path):
        return -1
    return os.path.getmtime(path)

def get_dir(path):
    return os.path.dirname(path)

def get_strict_dir(path):
    if path == '/':
        raise Exception("Cannot get parent directory of the root directory")
    if path[-1] == '/':
        path = path[:-1]
    folder, _ = os.path.split(path)
    return folder

def ensure_dir_exists(path):
    folder = get_dir(path)
    _ensure_dir_exists_help(folder)

def _ensure_dir_exists_help(path):
    if os.path.exists(path):
        return

    if path == "/":
        return

    parent = get_strict_dir(path)
    if parent == "":
        os.mkdir(path)
    else:
        _ensure_dir_exists_help(parent)
        os.mkdir(path)


