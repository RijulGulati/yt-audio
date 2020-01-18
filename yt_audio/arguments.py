import argparse
import ast

from .version import __version__


def get_args(config):
    """
    Get CLI arguments
    """

    _description = 'A simple, configurable youtube-dl wrapper for downloading and managing youtube audio.'
    _usage = '%(prog)s [OPTIONS] REQUIRED_ARGS'
    _conflict_handler = 'resolve'

    parser = argparse.ArgumentParser(
        description=_description, conflict_handler=_conflict_handler, usage=_usage)

    required = parser.add_argument_group('Required Arguments (Any/all)')

    required.add_argument("url_list", nargs='*',
                          help="Video/Playlist URL with (optional) save directory [URL::dir]",
                          metavar="URL[::DIR]")

    options = parser.add_argument_group('Optional Arguments')

    options.add_argument('-h', '--help', action='help',
                         help='show this help message and exit')
    options.add_argument('-v', '--version', action='version', version='%(prog)s {0}'.format(__version__),
                         help='show version and exit')
    options.add_argument("--use-archive", action='store_true', dest='use_archive',
                         help="use archive file to track downloaded titles")
    options.add_argument("--use-metadata", action='store_true', dest='use_metadata',
                         help="use metadata to track downloaded titles")
    options.add_argument("--output-format", dest='output_format',
                         nargs='?', help="File output format")
    options.add_argument("--ytdl-args", nargs='?', dest='ytdl_additional_args',
                         help="youtube-dl additional arguments")

    cargs = custom_args(config, required)
    args = vars(parser.parse_args())
    return args, cargs


def custom_args(config, required):
    dict_args = {}
    if 'url_list' in config and config['url_list']:
        custom_args_list = [x for x in ast.literal_eval(
            config['url_list'])]
        if len(custom_args_list) > 0:
            for arg in custom_args_list:
                short_arg = ast.literal_eval(arg.split('::')[0])[0]
                long_arg = ast.literal_eval(arg.split('::')[0])[1]
                help_text = ast.literal_eval(arg.split('::')[0])[2]
                required.add_argument(
                    short_arg, long_arg, help=help_text+' [Custom]', action='store_true')

                if len(arg.split('::')) == 3:
                    dict_args[long_arg.split(
                        '--')[1].replace('-', '_')] = arg.split('::')[1] + "::" + arg.split('::')[2]
                else:
                    dict_args[long_arg.split('--')[1]] = arg.split('::')[1]
            required.add_argument(
                "--all", dest='all_custom_args', help="All [Custom] Arguments", action='store_true')
    return dict_args
