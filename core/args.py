"""Argument management module."""

import argparse
import os

from core.detection import detect_file_type

from core.build_info import BuildInfo

parser = argparse.ArgumentParser(description='NeoXtractor')
parser.add_argument('--version', '-v',
                    action='version',
                    version=f'{BuildInfo.version if BuildInfo.version else "development"} (Build: {
                        BuildInfo.commit_hash[:7] if BuildInfo.commit_hash else "unknown"})')
parser.add_argument('--log-level',
                  help='Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL or integer values)',
                  dest='log_level')

_subparsers = parser.add_subparsers(help="subcommand help", dest="subcommand")

gui_parser = _subparsers.add_parser('gui', help='Run the NeoXtractor GUI')

wpk_parser = _subparsers.add_parser('wpk', help='Extract an IDX/WPK archive')
wpk_parser.add_argument('path', help='Path to IDX or WPK file')
wpk_parser.add_argument('wpk_path', nargs='?', help='Optional WPK file path if the first argument is IDX')
wpk_parser.add_argument('-o', '--output', dest='output', default='.', help='Output directory')
wpk_parser.add_argument('-k', '--key', dest='key', type=lambda x: int(x, 0), help='Decryption key (hex or int)')

arguments = argparse.Namespace()

def parse_args():
    """Parse arguments."""
    parser.parse_args(namespace=arguments)

    if arguments.subcommand == 'wpk':
        from core.wpk.wpk_file import WPKFile
        from core.wpk.class_types import WPKReadOptions

        idx_path = arguments.path
        wpk_path = arguments.wpk_path

        detected = detect_file_type(idx_path)
        if detected == 'wpk':
            wpk_path = idx_path
            idx_path = os.path.splitext(idx_path)[0] + '.idx'
        elif detected == 'idx' and wpk_path is None:
            wpk_path = os.path.splitext(idx_path)[0] + '.wpk'
        elif wpk_path and detect_file_type(wpk_path) == 'idx':
            idx_path, wpk_path = wpk_path, idx_path

        options = WPKReadOptions(decryption_key=arguments.key)
        with WPKFile(idx_path, wpk_path, options) as wpk_file:
            wpk_file.extract_all(arguments.output)
