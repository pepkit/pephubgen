import sys
from git import Repo
from git.exc import GitCommandError

from logging import getLogger
from .const import PACKAGE_NAME
import yaml
import os
import shutil

_LOGGER = getLogger(PACKAGE_NAME)

def download_peps(data_repo: str, out_path: str = "./data", overwrite: bool = False):
    """
    Download the repo and store in local storage for use
    """
    # check if already downloaded:
    if os.path.isdir(out_path):
        if overwrite:
            _LOGGER.info(f"Overwriting existing data storage path: {out_path}")
            shutil.rmtree(out_path)
        else: pass

    try:
        Repo.clone_from(
            data_repo,
            out_path,
        )

    # catch repo already downloaded if above
    # fails for some reason
    except GitCommandError as e:
        _LOGGER.error(f"Error fetching data: {e}")
        sys.exit(1)
    
    # catch else
    except Exception as err:
        print(f"Unexpected error occured: {err}")

def _is_valid_namespace(path: str, name: str) -> bool:
    """
    Check if a given path is a valid namespace directory. Function
    Will check a given path for the following criteria:
        1. Is a folder
        2. Is not a "dot" file (e.g. .git)
    """
    criteria = [
        os.path.isdir(path),
        not name.startswith(".")
    ]
    return all(criteria)

# attentive programmers will notice that this is identical
# to the function above. I am keeping them separate as in
# the future there might exist separate criteria for a
# namespace v a projects
def _is_valid_project(path: str, name: str) -> bool:
    """
    Check if a given project name is a valid project
    directory. Will check a given project for the following
    criteria:
        1. Is a folder
        2. Is not a "dot" file (e.g. .git)
    """
    criteria = [
        os.path.isdir(path),
        not name.startswith(".")
    ]
    return all(criteria)

def _extract_project_file_name(path_to_proj: str) -> str:
    """
    Take a given path to a PEP/project inside a namespace and
    return the name of the PEP configuration file. The process
    is completed in the following steps:
        1. Look for a .pephub.yaml file
            if exists -> check for config_file attribute
            else step two
        2. Look for project_config.yaml
            if exists -> return path
            else step 3
        3. If no .pephub.yaml file with config_file attribute exists AND
           no porject_config.yaml file exists, then return None.
    """
    try:
        with open(f"{path_to_proj}/.pephub.yaml", "r") as stream:
            _pephub_yaml = yaml.safe_load(stream)

        # check for config_file attribute
        if "config_file" in _pephub_yaml: return _pephub_yaml["config_file"]
        else: return None

    # catch no .pephub.yaml exists
    except FileNotFoundError:
        if not os.path.exists(f"{path_to_proj}/project_config.yaml"):
            return None
        else: return "project_config.yaml"

def load_data_tree(pep_storage_path: str) -> dict:
    """
    Once the data.pephub repo is downloaded, we can
    load the storage tree into memory by traversing
    the folder structure and storing locations to
    configuration files into the dictonary
    """

    if not os.path.isdir(pep_storage_path):
        raise FileNotFoundError(f"PEP data path not found: {pep_storage_path}")

    # init storage dict
    PEP_STORES = {}
    
    # traverse directory
    for name in os.listdir(pep_storage_path):
        # build a path to the namespace
        path_to_namespace = f"{pep_storage_path}/{name}"
        if _is_valid_namespace(path_to_namespace, name):
            # init sub-dict
            PEP_STORES[name] = {}

            # traverse projects
            for proj in os.listdir(path_to_namespace):
                # build path to project
                path_to_proj = f"{path_to_namespace}/{proj}"
                if _is_valid_project(path_to_proj, proj):
                    PEP_STORES[name][proj] = f"{path_to_proj}/{_extract_project_file_name(path_to_proj)}"

    return PEP_STORES