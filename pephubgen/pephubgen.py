""" Computing configuration representation """

import argparse
import logmuse
import sys
import tempfile

from .db import download_peps, load_data_tree
from .generator import Generator
from .const import PEPHUB_URL
from . import __version__


class _VersionInHelpParser(argparse.ArgumentParser):
    def format_help(self):
        """ Add version information to help text. """
        return "version: {}\n".format(__version__) + \
               super(_VersionInHelpParser, self).format_help()


def build_argparser():
    """
    Builds argument parser.

    :return argparse.ArgumentParser
    """

    banner = "%(prog)s - generate a static file representation of a PEP data repository."
    additional_description = "\n..."

    parser = _VersionInHelpParser(
            description=banner,
            epilog=additional_description)

    parser.add_argument(
            "-V", "--version",
            action="version",
            version="%(prog)s {v}".format(v=__version__))

    parser.add_argument(
            "-d", "--data", required=False,
            default=PEPHUB_URL,
            help="URL/Path to PEP storage tree.")
    
    parser.add_argument(
            "-o", "--out", required=False,
            default="./out",
            help="Outpath for generated PEP tree.")
    
    parser.add_argument(
            "-p", "--path", required=False,
            help="Path to serve the file server at."
    )

    # parser for serve command
    subparsers = parser.add_subparsers(
        help="Functions",
        dest="serve"
    )
    serve_parser = subparsers.add_parser("serve", help="Serve a directory using pythons built-in http library")
    serve_parser.set_defaults(
        func=serve_directory
    )
    serve_parser.add_argument(
        "-f", "--files", required=False,
        help="Files to serve.",
        default="./out"
    )

    return parser


def serve_directory(args):
    from http.server import HTTPServer, SimpleHTTPRequestHandler
    import os

    # remember current dir to return
    pwd = os.getcwd()

    _LOGGER.info("Serving files at http://localhost:8000")

    httpd = HTTPServer(('localhost', 8000), SimpleHTTPRequestHandler)
    try:
        os.chdir(args.files)
        httpd.serve_forever()
    except KeyboardInterrupt:
        os.chdir(pwd)
        _LOGGER.info("Goodbye.")
        sys.exit(0)

def main():
    """ Primary workflow """

    parser = logmuse.add_logging_options(
        build_argparser(),
    )
    args = parser.parse_args()
    
    global _LOGGER
    _LOGGER = logmuse.logger_via_cli(
        args, 
        make_root=True,
        fmt="[pephubgen] -----> %(message)s"
    )

    _LOGGER.info(f"Reading PEPs from {args.data}")

    # catch serve argument and
    # start server
    if args.serve:
        args.func(args)
    

    # else generate
    else:
        with tempfile.TemporaryDirectory() as tmp:
            # download peps
            download_peps(
                args.data,
                tmp
            )
            PEP_TREE = load_data_tree(tmp)

            # generate static files
            g = Generator()
            g.generate(
                PEP_TREE, 
                path=args.out
            )
    

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        _LOGGER.error("Program canceled by user!")
        sys.exit(1)