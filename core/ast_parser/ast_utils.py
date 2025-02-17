import os
import time
from functools import wraps


def method_decorator(func):
    """Decorator to measure and log execution time of methods."""
    @wraps(func)
    def wrapped(self, *args, **kwargs):
        start_time = time.time()
        result = func(self, *args, **kwargs)
        end_time = time.time()
        print(f"Function '{func.__name__}' executed in {end_time - start_time:.4f} seconds")
        return result
    return wrapped


def get_py_files(directory):
    """Retrieve all Python files from the specified directory."""
    py_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                py_files.append(os.path.join(root, file))
    return py_files


def convert_to_relative_path(root_path, working_path):
    """Convert absolute paths to relative paths based on a root directory."""
    return os.path.relpath(root_path, working_path)


def get_dotted_name(root_path, file_path):
    """Convert file paths to dotted Python module names."""
    if file_path.endswith('.py'):
        file_path = file_path[:-3]
    relative_path = os.path.relpath(file_path, root_path)
    return relative_path.replace(os.path.sep, '.')


def get_module_name(file_path, node, working_path):
    """Retrieve the module name from an ImportFrom node."""
    if node.module:
        return node.module

    levels_up = node.level
    current_dir = os.path.dirname(file_path)

    while levels_up > 0:
        current_dir = os.path.dirname(current_dir)
        levels_up -= 1

    return get_dotted_name(working_path, current_dir)


def module_name_to_path(module_name, working_path):
    """Convert a Python module name to a file system path."""
    relative_path = module_name.replace('.', os.path.sep)
    absolute_path = os.path.join(working_path, relative_path)
    return os.path.normpath(absolute_path)