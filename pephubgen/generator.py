from logging import getLogger
import os
import json
import peppy
from peppy.exceptions import PeppyError

from .const import PACKAGE_NAME
_LOGGER = getLogger(PACKAGE_NAME)

class Generator:
    def __init__(self):
        pass

    def _verify_path(self, path: str) -> None:
        """
        While generating the static files, a lot of
        path checking is going on, where if certain folders
        don't exist, they must be generated. This is a
        generic function to wrap that functionality.
        """
        if not os.path.exists(path):
            if self._verbose:
                _LOGGER.info(f"Generating directory at: {path}")
            os.makedirs(path)
    
    def _namespace_info(self, namespace: str):
        """
        Generate the information file for the given
        namespace at out_path/<namespace>/info
        """
        namespace_folder = f"{self._OUT_PATH}/{namespace}"
        self._verify_path(namespace_folder)
        if self._verbose:
            _LOGGER.info(f"Writing namespace info for {namespace}")

        # set up info package to write
        info = {
            'projects': [],
            'num_projects': 0
        }

        #load info package
        for proj in self._PEP_TREE[namespace]:
            info['projects'].append(proj)
            info['num_projects'] += 1
        
        # dump info to file
        with open(f"{namespace_folder}/{self._INFO_FILE_NAME}", "w") as f:
            f.write(
                json.dumps(info)
            )

    def _project_info(self, pep: peppy.Project, namespace: str, pep_id: str) -> None:
        """
        Generate the information file for a
        specific pep
        """
        pep_folder = f"{self._OUT_PATH}/{namespace}/{pep_id}"
        self._verify_path(pep_folder)
        if self._verbose:
            _LOGGER.info(f"Writing project info for {pep_id} ({namespace})")

        with open(f"{pep_folder}/{self._INFO_FILE_NAME}", "w") as f:
            info = pep.to_dict()
            f.write(
                json.dumps(str(info))
            )

    def generate(self, 
        pep_tree: dict, 
        path: str = "./",
        info_file_name: str = "info",
        verbose: bool = False
    ):
        """
        Generate the static files for the pephub
        static file server. Requires both a path
        to the desired location of the output and
        a dictionary that contains the pep storage.
        """
        # init params
        self._PEP_TREE = pep_tree
        self._OUT_PATH = path
        self._INFO_FILE_NAME = info_file_name
        self._verbose = verbose

        # init directory
        self._verify_path(self._OUT_PATH)

        # iterate over namespaces
        for namespace in self._PEP_TREE:
            self._namespace_info(namespace)
            # iterate over projects inside namespace
            for pep_id in self._PEP_TREE[namespace]:
                try:
                    proj = peppy.Project(self._PEP_TREE[namespace][pep_id])
                    self._project_info(proj, namespace, pep_id)
                except PeppyError as pe:
                    _LOGGER.warn(str(pe))
                    _LOGGER.warn(f"Skipping pep \"{pep_id}\" (in {namespace})... an error occured. See above. ")
                except Exception as e:
                    _LOGGER.warn(f"Unknown exception caught: {e}")
                    