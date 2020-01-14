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
            self.use_archive = False
            self.archive_file = ''

            self.yt_base_playlist_url = 'https://www.youtube.com/playlist'
            self.yt_base_url = 'https://www.youtube.com/watch?v='
            # --add-metadata is only required if youtube-dl's archive file is NOT used for
            # keeping track of existing records
            self.ytdl_required_args = '-x --print-json'
            self.resolve_input()
        except Exception as ex:
            self.common.log(str(ex), 'error')
            exit(1)

    def resolve_input(self):
        """
        Reads configuration file
        """
        try:
            self.url_list = self.common.get_value(
                self.config['DEFAULT'], self.args, 'url_list', self.custom_args)
            if not self.url_list:
                raise Exception(
                    "URL(s)/custom arguments required. Use --help for available options\n")
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
            self.use_archive = self.common.get_value(
                self.config['DEFAULT'], self.args, 'use_archive')

            if not self.common.ffprobe and self.common.avprobe:
                self.ffprobe_cmd.replace('ffprobe', 'avprobe')

            if 'ytdl_additional_args' in self.args and self.args['ytdl_additional_args']:
                _additional_args = self.args['ytdl_additional_args']
                _temp = self.download_cmd.split(' ')
                _temp.insert(1, _additional_args)

                self.download_cmd = ' '.join(_temp)

            if not self.use_archive and '--download-archive' not in self.download_cmd \
                    and '--add-metadata' in self.download_cmd:
                self.use_archive = False
            else:
                self.use_archive = True
                if '--download-archive' not in self.download_cmd:
                    _temp = self.download_cmd.split(' ')
                    _temp.insert(1, '--download-archive records.txt')
                    self.download_cmd = ' '.join(_temp)
                    self.archive_file = 'records.txt'
                else:
                    self.use_archive = True
                    self.archive_file = self.download_cmd.split(' ')[self.download_cmd.split(
                        ' ').index('--download-archive') + 1]

            _missed_req_args = [x for x in self.ytdl_required_args.split(
                ' ') if x not in self.download_cmd]

            if _missed_req_args:
                _message = 'The following youtube-dl arguments are mandatory for yt-audio to work: {0}'.format(
                    " ".join(_missed_req_args))
                if '--add-metadata' in _missed_req_args:
                    _message = _message + \
                        "\n\nNOTE: yt-audio by default uses file's metadata (--add-metadata) to keep track of already downloaded titles in a directory. Pass --ytdl-args \"--add-metadata\" to proceed. Alternatively, if you wish to use youtube-dl's archive file feature instead, pass --use-archive to yt-audio. Please read documentation for more info."
                raise Exception(_message)
        except Exception as ex:
            raise ex

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
                    _remote_url_list = [
                        self.yt_base_url+x["id"] for x in out["entries"]]
                    self.playlist_directory = str(
                        PurePath(self.output_directory, playlist_name))

                    self.common.log("Found {0} record(s) in [Remote] playlist '{1}'".format(
                        playlist_entries_count, playlist_name))
                    self.common.log('Save directory: {0}\n'.format(
                        self.playlist_directory))

                    if Path(self.playlist_directory).exists():
                        if not self.use_archive:
                            for title in Path(self.playlist_directory).iterdir():
                                audio_path = str(
                                    PurePath(self.playlist_directory, title.name))
                                _url = self.common.get_file_url(
                                    audio_path, self.ffprobe_cmd)
                                if _url is not None and _url in _remote_url_list:
                                    _remote_url_list.remove(_url)
                        else:
                            _archive_file = str(
                                PurePath(self.playlist_directory, self.archive_file))
                            _archive_file_content = self.common.read_archive(
                                _archive_file)
                            if _archive_file_content:
                                _archive_file_content = [
                                    (self.yt_base_url+x.split(' ')[1]).replace('\n', '') for x in _archive_file_content]
                                _remote_url_list = [
                                    x for x in _remote_url_list if x not in _archive_file_content]
                            self.download_cmd = self.download_cmd.replace(
                                self.archive_file, _archive_file)
                    else:
                        os.makedirs(self.playlist_directory)
                        if self.use_archive:
                            _archive_file = str(
                                PurePath(self.playlist_directory, self.archive_file))
                            self.download_cmd = self.download_cmd.replace(
                                self.archive_file, _archive_file)

                    if len(_remote_url_list) > 0:
                        self.common.log("{0} record(s) will be downloaded.".format(
                            len(_remote_url_list)))
                        _download_path = str(
                            PurePath(self.playlist_directory, self.output_format))
                        _download_command = self.download_cmd.replace(
                            "$OUTPUT$", _download_path).replace("$URL$", " ".join(_remote_url_list))

                        self.common.download_audio(
                            _download_command, len(_remote_url_list))
                    else:
                        self.common.log(
                            "Titles are already in sync.")
                    if self.use_archive and _archive_file in self.download_cmd:
                        self.download_cmd = self.download_cmd.replace(
                            _archive_file, self.archive_file)
                else:
                    self.common.log(
                        "\n[Single] Processing link {0}".format(url), 'info')
                    self.common.log(
                        'Save directory: {0}\n'.format(self.output_directory))
                    is_present = False
                    if self.use_archive:
                        _archive_file = str(PurePath(
                            self.output_directory, self.archive_file))
                        self.download_cmd = self.download_cmd.replace(
                            self.archive_file, _archive_file)
                        _archive_file_content = self.common.read_archive(
                            _archive_file)

                    if Path(self.output_directory).exists():
                        if not self.use_archive:
                            for title in Path(self.output_directory).iterdir():
                                audio_path = str(
                                    PurePath(self.output_directory, title.name))
                                _url = self.common.get_file_url(
                                    audio_path, self.ffprobe_cmd)
                                if _url is not None and _url == url:
                                    is_present = True
                                    break
                        else:
                            if _archive_file_content:
                                _archive_file_content = [
                                    (self.yt_base_url + x.split(' ')[1]).replace('\n', '') for x in _archive_file_content]
                                if url in _archive_file_content:
                                    is_present = True
                    else:
                        os.makedirs(self.output_directory)

                    if not is_present:
                        _download_path = str(
                            PurePath(self.output_directory, self.output_format))
                        _download_command = self.download_cmd.replace(
                            "$OUTPUT$", _download_path).replace("$URL$", url)
                        self.common.download_audio(
                            _download_command, len(url.split(' ')))
                    else:
                        self.common.log("Title is already present in directory '{0}'\n".format(
                            self.output_directory))
                    if self.use_archive and _archive_file in self.download_cmd:
                        self.download_cmd = self.download_cmd.replace(
                            _archive_file, self.archive_file)
        except StopIteration:
            pass
        except Exception as ex:
            self.common.log(str(ex), 'error')


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


if __name__ == "__main__":
    main()
