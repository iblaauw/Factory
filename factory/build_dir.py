import os
from .utils import ensure_dir_exists

known_files = set() # This set of files will not be placed in the build directory, but left at their normal path
build_dir = "build"

def translate_file(path):
    if path in known_files:
        return path

    current_dir = os.getcwd()
    abspath = os.path.abspath(path)

    if not abspath.startswith(current_dir):
        return path

    subpath = abspath[len(current_dir):]
    if subpath[0] == '/':
        subpath = subpath[1:]

    build_path = os.path.join(build_dir, subpath)
    ensure_dir_exists(build_path)
    return build_path

def set_build_dir(new_dir):
    global build_dir
    build_dir = new_dir

def get_build_dir():
    return build_dir

def ResetFiles():
    known_files.clear()
    global build_dir
    set_build_dir("build")



