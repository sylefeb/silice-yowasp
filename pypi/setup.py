from setuptools import setup
from setuptools_scm.git import parse as parse_git

def version():
    return "0.1"

setup(
    version=version(),
)
