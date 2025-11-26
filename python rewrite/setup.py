from setuptools import setup, Extension
from Cython.Build import cythonize

extensions = [
    Extension(
        "cython_main",
        ["cython_main.pyx"],
    ),
]

setup(
    ext_modules=cythonize(
        extensions,
        compiler_directives={
            "language_level": 3,  # Use Python 3 syntax (f-strings, etc.)
        },
    ),
)
