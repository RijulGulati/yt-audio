#!/usr/bin/env python3

import json
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
            self.use_metadata = False
            self.archive_file = ''

            self.yt_base_url = 'https://www.youtube.com/watch?v='
            self.ytdl_required_args = ['-x', '--print-json']
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
            self.use_metadata = self.common.get_value(
                self.config['DEFAULT'], self.args, 'use_metadata')

            if not self.common.ffprobe and self.common.avprobe:
                self.ffprobe_cmd.replace('ffprobe', 'avprobe')

            if self.use_metadata and self.use_archive:
                self.use_archive = True
                self.use_metadata = False

            if 'ytdl_additional_args' in self.args and self.args['ytdl_additional_args']:
                _additional_args = self.args['ytdl_additional_args']
                _temp = self.download_cmd.split(' ')
                _temp.insert(1, _additional_args)
                self.download_cmd = ' '.join(_temp)

            if self.use_metadata and '--add-metadata' not in self.download_cmd:
                self.ytdl_required_args.append('--add-metadata')

            if self.use_archive:
                if '--download-archive' not in self.download_cmd:
                    _temp = self.download_cmd.split(' ')
                    _temp.insert(1, '--download-archive records.txt')
                    self.download_cmd = ' '.join(_temp)
                    self.archive_file = 'records.txt'
                else:
                    self.archive_file = self.download_cmd.split(' ')[self.download_cmd.split(
                        ' ').index('--download-archive') + 1]

            _missed_req_args = [
                x for x in self.ytdl_required_args if x not in self.download_cmd]

            if _missed_req_args:
                _message = 'The following youtube-dl arguments are mandatory: {0}\n'.format(
                    " ".join(_missed_req_args))
                raise Exception(_message)
        except Exception as ex:
            raise ex

    def filter_download_urls(self, path, url_list, archive_file=''):
        """
        Filter URL(s) to download based on tracking method
        """
        urls_to_download = []
        if Path(path).exists():
            if self.use_archive:
                _archive_path = str(PurePath(path, archive_file))
                _archive_file_content = self.common.read_archive(_archive_path)
                if _archive_file_content:
                    _archive_file_content = [
                        (self.yt_base_url+x.split(' ')[1]).replace('\n', '') for x in _archive_file_content]
                    urls_to_download = [
                        x for x in url_list if x not in _archive_file_content]
                    return urls_to_download
                else:
                    return url_list
            elif self.use_metadata:
                for title in Path(path).iterdir():
                    audio_path = str(PurePath(path, title.name))
                    _url = self.common.get_file_url(
                        audio_path, self.ffprobe_cmd)
                    if _url and _url not in url_list:
                        urls_to_download.append(_url)
                return urls_to_download
            else:
                return url_list
        else:
            return url_list

    def yt_audio(self):
        """
        Main method. This method controls the entire program's logic.
        """
        try:
            _audio_directory = self.output_directory
            for url in self.url_list:
                _remote_url_list = []
                url = url.replace('\\', '')
                self.output_directory = _audio_directory
                if len(url.split("::")) > 1:
                    self.output_directory = url.split("::")[1]
                    url = url.split("::")[0]
                command = self.playlist_info_cmd.replace("$PLAYLIST_URL$", url)
                print()
                self.common.log(
                    "Fetching info for URL '{0}'".format(url), 'info')
                out = next(self.common.ExecuteCommand(command))
                try:
                    out = json.loads(out)
                except json.JSONDecodeError:
                    self.common.log(
                        "{0} is not a valid url. Please check and try again.".format(url), 'error')
                    continue

                url_title = out["title"]
                # Check if URL is playlist
                if 'entries' in out:
                    playlist_entries_count = len(out["entries"])
                    _remote_url_list = [self.yt_base_url+x["id"]
                                        for x in out["entries"]]
                    self.output_directory = str(
                        PurePath(self.output_directory, url_title))
                    self.common.log("Found {0} record(s) in [Remote] playlist '{1}'".format(
                        playlist_entries_count, url_title))
                    self.common.log('Save directory: {0}\n'.format(
                        self.output_directory))
                else:
                    # URL is single record
                    _remote_url_list.append(url)
                    self.common.log('{0} (Save Directory: {1})\n'.format(
                        url_title, self.output_directory))

                urls_to_download = self.filter_download_urls(
                    self.output_directory, _remote_url_list, self.archive_file)

                if len(urls_to_download) > 0:
                    self.common.log("{0} record(s) will be downloaded.".format(
                        len(urls_to_download)))
                    _download_path = str(
                        PurePath(self.output_directory, self.output_format))
                    _download_command = self.download_cmd.replace(
                        "$OUTPUT$", _download_path).replace("$URL$", " ".join(urls_to_download))
                    if self.use_archive:
                        _archive_path = str(
                            Path(self.output_directory, self.archive_file))
                        _download_command = _download_command.replace(
                            self.archive_file, _archive_path)
                    self.common.download_audio(
                        _download_command, len(_remote_url_list))
                else:
                    self.common.log("Title(s) are already in sync.\n")
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
