import factory
import sys
import importlib
import importlib.util
from pathlib import Path
import traceback
import contextlib
from contextlib import redirect_stdout
import filecmp
import os

class TestContext(object):
    def __init__(self):
        self.num_run = 0
        self.num_passed = 0
        self.failed = []
        self.untestable = []

    def success(self, name):
        self.num_run += 1
        self.num_passed += 1
        print("{} passed!".format(name))

    def fail(self, name, reason=None):
        self.num_run += 1
        self.failed.append(name)
        reason_str = "" if reason is None else reason
        print("{} failed. {}".format(name, reason_str), file=sys.stderr)

    def fail_except(self, name):
        self.num_run += 1
        self.failed.append(name)
        print("{} failed. The test threw an exception:\n".format(name), file=sys.stderr)
        traceback.print_exc()

    def fatal(self, name, reason):
        self.untestable.append(name)
        print("Test {} could not be run. {}".format(name, reason), file=sys.stderr)

    def fatal_except(self, name):
        self.untestable.append(name)
        print("Test {} could not be run. An exception was encountered while attempting to load the test.\n".format(name))
        traceback.print_exc()

    def print_stats(self):
        print("*" * 20)
        print("{} / {} tests succeeded".format(self.num_passed, self.num_run))
        if len(self.failed) > 0:
            print()
            print("The following tests failed:")
            for name in self.failed:
                print("    {} failed".format(name))

        if len(self.untestable) > 0:
            print()
            print("The following tests could not be run:")
            for name in self.untestable:
                print("    {}".format(name))

class TestAssertionException(Exception):
    pass

class TestUtils(object):
    def Assert(self, value, message=None):
        if not value:
            if message is None:
                to_display = "Assertion failed!"
            else:
                to_display = "Assertion failed: {}".format(message)
            print(to_display)
            raise TestAssertionException(to_display)

    def EnsureExists(self, path, is_dir=False):
        if isinstance(path, str):
            path = Path(path)

        name = str(path)
        self.Assert(path.exists(), "File '{}' not found".format(name))

        if is_dir:
            self.Assert(path.is_dir(), "File '{}' is not a directory".format(name))
        else:
            self.Assert(path.is_file(), "File '{}' is a directory".format(name))

    def EnsureNotExists(self, path):
        if isinstance(path, str):
            path = Path(path)

        self.Assert(not path.exists(), "File '{}' should be deleted".format(path))


def Test(name, path, context):
    print("Running test {}...".format(name))
    to_run = path / "make.py"
    master = path / "master.txt"
    output = path / "output.txt"

    if not to_run.exists() or not to_run.is_file():
        context.fatal(name, "Could not find make.py in test folder")
        return

    if not master.exists() or not master.is_file():
        context.fatal(name, "Could not find master.txt in test folder")
        return

    try:
        DoTest(name, to_run, master, output, context)
    except Exception:
        context.fatal_except(name)

def DoTest(name, to_run, master, output, context):
    importlib.reload(factory)
    module = import_file_from_path(to_run)
    module.factory = factory
    module.test_utils = TestUtils()
    func = module.main

    with output.open(mode='w') as out_file:
        try:
            with redirect_stdout(out_file), push_cd(to_run.parent):
                func()
        except TestAssertionException as ex:
            context.fail(name, str(ex))
            return
        except Exception:
            context.fail_except(name)
            return

    if not filecmp.cmp(str(master), str(output)):
        context.fail(name, "Output does not match master file")
        return

    context.success(name)


def import_file_from_path(path_obj):
    name = path_obj.stem
    spec = importlib.util.spec_from_file_location(name, str(path_obj))
    module = spec.loader.load_module()
    return module

@contextlib.contextmanager
def push_cd(path):
    if not isinstance(path, str):
        path = str(path)

    current_dir = os.getcwd()
    os.chdir(path)

    try:
        yield
    finally:
        os.chdir(current_dir)


def main():
    context = TestContext()
    testdir = Path("tests")
    assert(testdir.exists() and testdir.is_dir())

    for entry in testdir.iterdir():
        if not entry.is_dir():
            continue

        name = entry.name
        Test(name, entry, context)
    context.print_stats()



if __name__ == "__main__":
    main()

