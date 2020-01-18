import configparser
import json
import os
import subprocess
from pathlib import Path, PurePath


class Common:
    """
    Common class
    """

    DEFAULT_ARGUMENT_VALUES = {
        'download_command': 'youtube-dl -x -q --print-json --audio-format mp3 --audio-quality 0 '
                            '--add-metadata --embed-thumbnail -o "$OUTPUT$" $URL$',
        'playlist_info_command': 'youtube-dl --flat-playlist -J $PLAYLIST_URL$',
        'output_format': '%%(title)s.%%(ext)s',
        'ffprobe_command': 'ffprobe -v quiet -print_format json -show_format -hide_banner "$PATH$"',
        'output_directory': str(PurePath(Path.home(), "Music"))
    }

    def __init__(self):
        self.ffprobe = True
        self.avprobe = True

    def ExecuteCommand(self, command, is_shell=False, single_line=False):
        """
        Executes command as a new process and returns response

        Parameters:
        ==========

        > command (string): command to execute.

        > is_shell (bool): Controls 'shell' paramater passed to subprocess.Popen().

        > single_line (bool): Whether to read single line or multiple lines.

        Returns:
        =======
        > (yield) command's stdout output
        """
        try:
            if command:
                if not is_shell:
                    command = command.split(" ")
                process = subprocess.Popen(
                    command, shell=is_shell, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

                while True:
                    if not single_line:
                        result = process.stdout.readlines()
                        result = ''.join([str(x, 'utf-8') for x in result])
                    else:
                        result = process.stdout.readline()
                    if not result:
                        break
                    yield result
        except Exception as ex:
            raise ex

    def get_file_url(self, path, command):
        """
        Reads file's metadata and returns URL

        Parameters:
        ==========

        > path (string): Absolute file path

        > command (string): ffprobe command to get purl from file

        Returns:
        =======
        > (string) URL
        """
        try:
            result = next(self.ExecuteCommand(
                command.replace('$PATH$', path), True))
            result = json.loads(result)
            return result['format']['tags']['purl']
        except KeyError:
            return None

    def download_audio(self, download_command, title_count):
        """
        Downloads file to specified path

        Parameters:
        ==========
        > download_command (string): youtube-dl download command

        > title_count (int): no. of titles to download
        """
        try:
            count = 1
            print("Download begin\n")
            for download in self.ExecuteCommand(download_command, True, True):
                print("[{0}/{1}] ".format(count, title_count) +
                      json.loads(download)["title"])
                count = count + 1
            print("\nDownload complete!\n")
        except json.JSONDecodeError as ex:
            self.log(ex.doc, 'error')
        except Exception as ex:
            raise ex

    def get_configfile_path(self, config_custom_path):
        """
        Get configuration file absolute path
        """
        try:
            if not config_custom_path:
                file_path = str(PurePath("yt-audio", "config.ini"))
                path = os.environ["XDG_CONFIG_HOME"]
                path = str(PurePath(path, file_path))
                return path
            else:
                return config_custom_path
        except KeyError:
            config_path = PurePath(Path.home(), ".config")
            path = str(PurePath(config_path, file_path))
            return path

    def read_config(self, config_custom_path=''):
        """
        Read config file and return result as dictionary
        """
        path = self.get_configfile_path(config_custom_path)
        config = configparser.ConfigParser()
        config.read(path)
        return dict(config)

    def log(self, message, message_type='message'):
        """
        Log (print) messages to stdout
        TODO: Log to file and use stderr for logging error messages

        Parameters:
        ==========
        > message (string): Message to log

        > message_type (string)(optional): Type of message ('error'/'warning'/'info'/[empty=unformatted])
        """
        if message_type == 'error':
            if 'ERROR' in message:
                message = message.replace('ERROR:', '\033[31mError:\033[0m')
                print('{0}'.format(message))
            else:
                print("\033[31mError:\033[0m {0}".format(message))
        elif message_type == 'info':
            print('\033[36m{0}\033[0m'.format(message))
        elif message_type == 'warning':
            print("\033[33mWarning:\033[0m {0}".format(message))
        else:
            print('{0}'.format(message))

    def get_value(self, config, args, key, custom_args=None):
        """
        Get input value(s) required by program for execution

        Parameters:
        ==========
        > config (dict): Configuration file.

        > args (dict): CLI arguments.

        > key (str): key to search in dict

        > custom_args (dict)(optional): CLI custom arguments.

        Returns:
        =======
        > (list/string) required value(s)
        """
        try:
            if key == 'url_list':
                if 'all_custom_args' in args and args['all_custom_args']:
                    _url_list = [custom_args[x] for x in custom_args]
                else:
                    _url_list = [custom_args[x]
                                 for x in custom_args if args[x]]
                if args[key]:
                    _url_list = _url_list + args[key]
                return _url_list

            if key in args and args[key]:
                return args[key]
            elif key in config and config[key]:
                if config[key] == '1':
                    return True
                elif config[key] == '0':
                    return False
                else:
                    return config[key]
            elif key in self.DEFAULT_ARGUMENT_VALUES:
                return self.DEFAULT_ARGUMENT_VALUES[key]
            else:
                return None
        except KeyError:
            pass

    def check_dependencies(self):
        _dependencies = ["ffmpeg -version|avconv -version",
                         "ffprobe -version|avprobe -version",
                         "youtube-dl --version",
                         ]
        for _dep in _dependencies:
            try:
                if len(_dep.split('|')) > 1:
                    _not_found = []
                    for opt in _dep.split('|'):
                        try:
                            res = next(self.ExecuteCommand(opt))
                            if res:
                                break
                        except FileNotFoundError:
                            _file = opt.split(' ')[0]
                            _not_found.append(_file)
                            if _file == 'ffprobe':
                                self.ffprobe = False
                            elif _file == 'avprobe':
                                self.avprobe = False
                            pass
                    if len(_not_found) == len(_dep.split('|')):
                        self.log('Either of {0} required. Please install and try again.\n'.format(
                            '/'.join(_not_found)), 'error')
                        exit(1)

                else:
                    next(self.ExecuteCommand(_dep))
            except FileNotFoundError:
                self.log('{0} not found. Please install {0} and try again.\n'.format(
                    _dep.split(' ')[0]), 'error')
                exit(1)
            except Exception as ex:
                raise ex

    def read_archive(self, archive_file):
        try:
            with open(archive_file) as archive:
                data = archive.readlines()
                return data
        except FileNotFoundError as ex:
            self.log(ex.filename + ': ' + ex.strerror, 'warning')
            self.log("> New archive file '{0}' will be created\n".format(
                ex.filename), 'info')
            return None
