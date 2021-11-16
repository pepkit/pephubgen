from logging import getLogger
import os
import peppy

from .const import PACKAGE_NAME
_LOGGER = getLogger(PACKAGE_NAME)

class Generator:
    def __init__(self,):
        pass

    def _verify_path(self, path: str) -> None:
        """
        While generating the static files, a lot of
        path checking is going on, where if certain folders
        don't exist, they must be generated. This is a
        generic function to wrap that functionality.
        """
        if not os.path.exists(path):
            _LOGGER.info(f"Generating directory at: {path}")
            os.makedirs(path)
    
    def _namespace_info(self, namespace: str):
        """
        Generate the information file for the given
        namespace at out_path/<namespace>/info
        """
        namespace_folder = f"{self._OUT_PATH}/{namespace}"
        self._verify_path(namespace_folder)
        _LOGGER.info(f"Writing namespace info for {namespace}")

        for proj in self._PEP_TREE[namespace]:
            proj_folder = f"{self._OUT_PATH}/{namespace}/{proj}"
            self._verify_path(proj_folder)

            with open (f"{self._OUT_PATH}/{namespace}/{proj}/info", "w") as f:
                f.write("stuff")

    def generate(self, PEP_TREE: dict, path: str = "./"):
        """
        Generate the static files for the pephub
        static file server. Requires both a path
        to the desired location of the output and
        a dictionary that contains the pep storage.
        """
        # init params
        self._PEP_TREE = PEP_TREE
        self._OUT_PATH = path

        # initialize the out directory
        if not os.path.exists(self._OUT_PATH):
            _LOGGER.info(f"Initializing new directory at {self._OUT_PATH}")
            os.makedirs(self._OUT_PATH)

        # iterate over namespaces
        for namespace in PEP_TREE:
            self._namespace_info(namespace)