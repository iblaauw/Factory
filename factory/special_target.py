from .utils import get_num_params

special_target_dict = {} # Mapping from target name to functions
                         # If this target is ever executed, the normal build process is ignored, and
                         # instead the function is just executed. An example of this is the 'clean' target.

def special_target(name):
    def decorator(func):
        num_params = get_num_params(func)
        if num_params != 1:
            raise Exception("A special target must take exactly one argument, which is the target to be built")
        special_target_dict[name] = func
        return func
    return decorator

def ResetSpecial():
    special_target_dict.clear()

