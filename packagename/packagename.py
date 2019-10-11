""" Computing configuration representation """

import argparse
import logmuse
import os
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

    banner = "%(prog)s - randomize BED files"
    additional_description = "\n..."

    parser = _VersionInHelpParser(
            description=banner,
            epilog=additional_description)

    parser.add_argument(
            "-V", "--version",
            action="version",
            version="%(prog)s {v}".format(v=__version__))

    parser.add_argument(
            "-i", "--input", required=True,
            help="File path to input file.")

    parser.add_argument(
            "-p", "--parameter", type=int, default=0,
            help="Some parameter.")

    return parser




def main():
    """ Primary workflow """

    parser = logmuse.add_logging_options(build_argparser())
    args = parser.parse_args()
    global _LOGGER
    _LOGGER = logmuse.logger_via_cli(args, make_root=True)

    msg = "Input: {input}; Parameter: {parameter}"
    _LOGGER.info(msg.format(input=args.input, parameter=args.parameter))

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        _LOGGER.error("Program canceled by user!")
        sys.exit(1)