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
    
    def _namespace_info(self, path: str):
        """
        Generate the information file for the given
        namespace at out_path/<namespace>/info
        """
        # extract namespace from the path
        namespace = path.split("/")[-1]

        if self._verbose:
            _LOGGER.info(f"Writing namespace info for {path}")

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
        with open(f"{path}/{self._INFO_FILE_NAME}", "w") as f:
            f.write(
                json.dumps(info)
            )

    def _project_info(
        self, 
        pep: peppy.Project, 
        path: str
    ) -> None:
        """
        Generate the information file for a
        specific pep
        """
        if self._verbose:
            _LOGGER.info(f"Writing project info for {path})")

        with open(f"{path}/{self._INFO_FILE_NAME}", "w") as f:
            info = pep.to_dict()
            f.write(
                json.dumps(info)
            )
    
    def _project_samples_info(self, proj: peppy.Project, path: str) -> None:
        """
        Generate an information file about a projects
        samples
        """
        if self._verbose:
            _LOGGER.info(f"Writing info on all samples for {path})")

        # init info package
        info = {
            "samples": [],
            "num_samples": 0
        }

        # load info package
        for sample in proj.samples:
            info['samples'].append(sample)
            info['num_samples'] += 1

        # write info package
        with open(f"{path}/{self._INFO_FILE_NAME}", "w") as f:
            f.write(
                json.dumps(str(info))
            )
    
    def _sample_info(self, sample: peppy.Sample, path: str) -> None:
        """
        Generate and write sample information to file
        """
        if self._verbose:
            _LOGGER.info(f"Writing sample info for {path})")

        # extract out a sample name
        try:
            sname = sample.sample_name
        except AttributeError:
            sname = sample.sample_id

        with open(f"{path}/{sname}{self._FILE_EXTENSION}", "w") as f:
            info = sample.to_dict()
            f.write(
                json.dumps(info)
            )

    def generate(
        self, 
        pep_tree: dict, 
        path: str = "./",
        info_file_name: str = "README",
        file_extenstion: str = ".json",
        verbose: bool = False,
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
        self._FILE_EXTENSION = file_extenstion
        self._INFO_FILE_NAME = info_file_name + file_extenstion
        self._verbose = verbose

        # init directory
        self._verify_path(self._OUT_PATH)

        # iterate over namespaces
        for namespace in self._PEP_TREE:
            # generate namespace folder
            path_to_namespace = f"{self._OUT_PATH}/{namespace}"
            self._verify_path(path_to_namespace)

            # generate info for namespace
            self._namespace_info(path_to_namespace)
            # iterate over projects inside namespace
            for pep_id in self._PEP_TREE[namespace]:
                # generate pep folder inside namespace
                path_to_pep = f"{path_to_namespace}/{pep_id}"
                self._verify_path(path_to_pep)

                # attempt to load the pep
                try:
                    proj = peppy.Project(self._PEP_TREE[namespace][pep_id])
                    self._project_info(proj, path_to_pep)
                # catch PeppyErrors
                except PeppyError as pe:
                    _LOGGER.warn(str(pe))
                    _LOGGER.warn(f"Skipping pep \"{pep_id}\" (in {namespace})... an error occured. See above. ")
                # catch else
                except Exception as e:
                    _LOGGER.warn(f"Unknown exception caught: {e}")

                # generate full sample info for a project
                path_to_samples = f"{path_to_pep}/samples"
                self._verify_path(path_to_samples)
                self._project_samples_info(proj, path_to_samples)

                # iterate over samples in a project
                for sample in proj.samples:
                    self._sample_info(sample, path_to_samples)

                    