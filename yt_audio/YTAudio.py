#!/usr/bin/env python3

import json
import os
import sys
from pathlib import Path, PurePath

from .arguments import get_args
from .common import Common


class YTAudio:
    """
    YTAudio Class. Program execution begins here.
    """

    def __init__(self):
        try:
            self.common = Common()
            self.config = self.common.read_config()
            self.args, self.custom_args = get_args(self.config['DEFAULT'])
            self.common.check_dependencies()
            self.url_list = []
            self.output_format = ''
            self.playlist_info_cmd = ''
            self.playlist_directory = ''
            self.output_directory = ''

            self.yt_base_playlist_url = 'https://www.youtube.com/playlist'
            self.yt_base_url = 'https://www.youtube.com/watch?v='
            self.ytdl_required_args = '--add-metadata -x --print-json'
            self.resolve_input()
        except Exception as ex:
            self.common.log(str(ex), 'error')
            exit(1)

    def yt_audio(self):
        """
        Main method. This method controls the entire program's logic.
        """
        try:
            _audio_directory = self.output_directory
            for url in self.url_list:
                url = url.replace('\\', '')
                self.output_directory = _audio_directory
                if len(url.split("::")) > 1:
                    self.output_directory = url.split("::")[1]
                    url = url.split("::")[0]
                if self.common.is_playlist(url, self.yt_base_playlist_url):
                    self.common.log(
                        "\n[Playlist] Processing link {0}".format(url), 'info')
                    self.common.log('Fetching playlist info...\n')
                    command = self.playlist_info_cmd.replace(
                        "$PLAYLIST_URL$", url)
                    out = next(self.common.ExecuteCommand(command))
                    try:
                        out = json.loads(out)
                    except json.JSONDecodeError:
                        self.common.log(
                            "{0} is not a valid url. Please check and try again.".format(url), 'error')
                        continue

                    playlist_name = out["title"]
                    playlist_entries_count = len(out["entries"])
                    remote_url_list = [
                        self.yt_base_url+x["id"] for x in out["entries"]]
                    self.playlist_directory = str(
                        PurePath(self.output_directory, playlist_name))

                    self.common.log("Found {0} record(s) in [Remote] playlist '{1}'".format(
                        playlist_entries_count, playlist_name))
                    self.common.log('Save directory: {0}\n'.format(
                        self.playlist_directory))

                    if Path(self.playlist_directory).exists():
                        for title in Path(self.playlist_directory).iterdir():
                            audio_path = str(
                                PurePath(self.playlist_directory, title.name))
                            _url = self.common.get_file_url(
                                audio_path, self.ffprobe_cmd)
                            if _url is not None and _url in remote_url_list:
                                remote_url_list.remove(_url)
                    else:
                        os.makedirs(self.playlist_directory)

                    if len(remote_url_list) > 0:
                        self.common.log("{0} record(s) will be downloaded.".format(
                            len(remote_url_list)))
                        _download_path = str(
                            PurePath(self.playlist_directory, self.output_format))
                        _download_command = self.download_cmd.replace(
                            "$OUTPUT$", _download_path).replace("$URL$", " ".join(remote_url_list))

                        self.common.download_audio(
                            _download_command, len(remote_url_list))
                    else:
                        self.common.log(
                            "Titles are already in sync.")
                else:
                    self.common.log(
                        "\n[Single] Processing link {0}".format(url), 'info')
                    is_present = False
                    if Path(self.output_directory).exists():
                        for title in Path(self.output_directory).iterdir():
                            audio_path = str(
                                PurePath(self.output_directory, title.name))
                            _url = self.common.get_file_url(
                                audio_path, self.ffprobe_cmd)
                            if _url is not None and _url == url:
                                is_present = True
                                break
                    else:
                        os.makedirs(self.output_directory)
                    if not is_present:
                        self.common.log(
                            'Save directory: {0}\n'.format(self.output_directory))
                        _download_path = str(
                            PurePath(self.output_directory, self.output_format))
                        _download_command = self.download_cmd.replace(
                            "$OUTPUT$", _download_path).replace("$URL$", url)
                        self.common.download_audio(
                            _download_command, len(url.split(' ')))
                    else:
                        self.common.log("Title is already present in directory '{0}'\n".format(
                            self.output_directory))
        except StopIteration:
            pass
        except Exception as ex:
            self.common.log(str(ex), 'error')

    def resolve_input(self):
        """
        Reads configuration file
        """
        try:
            self.url_list = self.common.get_value(
                self.config['DEFAULT'], self.args, 'url_list', self.custom_args)
            self.output_format = self.common.get_value(
                self.config['DEFAULT'], self.args, 'output_format').replace('%%', '%')
            self.output_directory = self.common.get_value(
                self.config['DEFAULT'], self.args, 'output_directory')
            self.playlist_info_cmd = self.common.get_value(
                self.config['DEFAULT'], self.args, 'playlist_info_command')
            self.ffprobe_cmd = self.common.get_value(
                self.config['DEFAULT'], self.args, 'ffprobe_command')
            self.download_cmd = self.common.get_value(
                self.config['DEFAULT'], self.args, 'download_command')

            if not self.url_list:
                raise Exception(
                    "URL(s)/custom arguments required. Use --help for available options")

            _missed_req_args = [x for x in self.ytdl_required_args.split(
                ' ') if x not in self.download_cmd]

            if _missed_req_args:
                raise Exception(
                    'The following youtube-dl arguments are mandatory for yt-audio to work: {0}'.format(
                        " ".join(_missed_req_args)))
        except Exception as ex:
            raise ex


def main():
    try:
        ytaudio = YTAudio()
        ytaudio.yt_audio()
    except KeyboardInterrupt:
        print("\nInterrupted by user. Aborting!\n")
        sys.exit(1)
    except Exception as ex:
        print("\nError: " + str(ex) + "\n")
        sys.exit(1)


# if __name__ == "__main__":
#     main()
