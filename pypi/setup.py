from setuptools import setup
from setuptools_scm.git import parse as parse_git
import subprocess
import os

def commit_count(path):
  repo_path    = os.path.abspath(path)
  commit_count = subprocess.check_output(["git", "rev-list", "--count", "HEAD"], cwd=repo_path).strip().decode("utf-8")
  return commit_count

def version():
  # for now, a straight-forward version string the increases with commit count
  count1 = commit_count("../silice-src")
  count2 = commit_count("..")
  return f"1.0.post{count1}{count2}"

setup(version=version())
