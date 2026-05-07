from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy

# List all C sources and your main .pyx file here
ext = Extension(
    name="engine",
    sources=[
        "engine.py",
        "main.py",
        "evaluator.py",
        "pst.py",
        "perf.py",
        "config.py",
    ],
    include_dirs=[numpy.get_include()]
)

setup(
    ext_modules=cythonize([ext])
)
