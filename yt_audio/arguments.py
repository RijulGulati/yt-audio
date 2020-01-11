import argparse
import ast


class Arguments:

    def get_args(self, config):
        """
        Get CLI arguments
        """
        self.parser = argparse.ArgumentParser(prog='yt-audio'
                                              "A simple youtube-dl wrapper for downloading and managing youtube audio",
                                              usage='yt-audio [OPTIONS] [URL[::DIR] [URL[::DIR]...] and/or CUSTOM_ARGUMENT [CUSTOM_ARGUMENT...]]')

        self.parser.add_argument("url_list", nargs='*',
                                 help="Video/Playlist URL with (optional) save directory [URL::dir]",
                                 metavar="URL[::DIR]")

        self.parser.add_argument("--ffprobe-command",
                                 nargs='?', help="ffprobe command")

        self.parser.add_argument("--output-format",
                                 nargs='?', help="File output format")

        self.parser.add_argument("--playlist-info-command",
                                 nargs='?', help="Fetch playlist info")

        self.parser.add_argument("--download-command", nargs='?',
                                 help="youtube-dl audio download command")

        custom_args = self.get_custom_args(config)
        args = vars(self.parser.parse_args())
        return args, custom_args

    def get_custom_args(self, config):
        dict_args = {}
        if 'url_list' in config and config['url_list']:
            custom_args_list = [x for x in ast.literal_eval(
                config['url_list'])]
            if len(custom_args_list) > 0:
                custom_args = self.parser.add_argument_group(
                    "custom arguments", "Custom Arguments generated from Config File")
                for arg in custom_args_list:
                    short_arg = ast.literal_eval(arg.split('::')[0])[0]
                    long_arg = ast.literal_eval(arg.split('::')[0])[1]
                    help_text = ast.literal_eval(arg.split('::')[0])[2]
                    custom_args.add_argument(
                        short_arg, long_arg, help=help_text, action='store_true')

                    if len(arg.split('::')) == 3:
                        dict_args[long_arg.split(
                            '--')[1].replace('-', '_')] = arg.split('::')[1] + "::" + arg.split('::')[2]
                    else:
                        dict_args[long_arg.split('--')[1]] = arg.split('::')[1]
                custom_args.add_argument(
                    "--all", help="All Custom Arguments", action='store_true')
        return dict_args
