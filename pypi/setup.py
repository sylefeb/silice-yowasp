from setuptools import setup
from setuptools_scm.git import parse as parse_git
import subprocess
import os

def version():
  # for now, a straight-forward version string the increases with commit count
  repo_path = os.path.abspath("../silice-src")
  commit_count = subprocess.check_output(["git", "rev-list", "--count", "HEAD"], cwd=repo_path).strip().decode("utf-8")
  return f"1.0.post{commit_count}"

setup(version=version())
