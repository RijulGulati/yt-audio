# yt-audio
A simple, configurable, cross-platform youtube-dl wrapper for downloading and managing youtube audio (with added features).


## Installation
- Requires [Python3](https://www.python.org/downloads/) (>=3.5), [youtube-dl](https://github.com/ytdl-org/youtube-dl) and [ffmpeg](https://www.ffmpeg.org/)/[avconv](https://libav.org/) as dependencies.

yt-audio can be installed via [pip](pip_link_here). Arch Linux users can use [AUR](link) as well.

`$ [sudo] pip3 install --upgrade yt-audio`

## Description and Features
yt-audio is a command-line program that is used download and manage audio from youtube.com. It is a youtube-dl wrapper program, which means it uses youtube-dl as backend for downloading audio. yt-audio tries to make audio/playlist management easy for users. It is cross-platform (Windows/Linux/MacOS).

### Features
- Configure/Setup your own command-line arguments for managing titles/playlists (See [usage](link) below)
- Ability to save each audio/playlist to a different directory (directory specified in argument).
- Option to keep track of already-downloaded playlist titles **with or without archive file**.
- Manage single/playlist audio(s).


## Usage
    usage: YTAudio.py [OPTIONS] REQUIRED_ARGS

    A simple, configurable youtube-dl wrapper for downloading and managing youtube audio.

    Required Arguments (Any/all):
    URL[::DIR]            Video/Playlist URL with (optional) save directory [URL::dir]
    -e, --example1        Example playlist [Custom]
    --all                 All [Custom] Arguments

    Optional Arguments:
    -h, --help            show this help message and exit
    -v, --version         show version and exit
    --use-archive         use archive file to track downloaded titles
    --use-metadata        use metadata to track downloaded titles
    --output-format [OUTPUT_FORMAT]
                            File output format
    --ytdl-args [YTDL_ADDITIONAL_ARGS]
                            youtube-dl additional arguments

**yt-audio requires either URL or custom argument(s) (or both) as mandatory input(s).**

### Custom Arguments
yt-audio gives user the ability to setup their own custom arguments for managing/synchronizing audio/playlists. Custom arguments can be configured in yt-audio's *(config.ini)* configuration file.

**NOTE (pip users): The user, if required, will have to copy the [configuration file](https://github.com/pseudoroot/yt-audio/blob/development/config.ini) as it is not copied during installation.**

**Unix/Linux Users:**
The default config location is **$XDG_CONFIG_HOME/yt-audio/** directory. In case *$XDG_CONFIG_HOME* is not set, the file can be placed in **$HOME/.config/yt-audio/** directory.

**Windows Users:** The default config location is **C:\\Users\\\<user>\\.config\\yt-audio**

**Setting up custom arguments**

The config file *config.ini* has URL_LIST[] option where users can specify arguments with corresponding URL and (optional) save directory. It's format is as follows:

    URL_LIST = [
                    # "['-short_arg1','--long_arg1','Help Text/Description']::URL::PATH"

                    # PATH (optional) specifies output directory for that particular playlist
                    # PATH should be absoulte directory path
                    # URL: Complete youtube title/playlist URL
                    # These arguments are visible in --help

                    # "['-e','--example1','Example playlist']::URL::PATH",
               ]

URL_LIST takes comma-separated string values. Each string value is formed from 3 components:

- CLI Argument - Argument to register. It is written in form: ['-short_arg','--long_arg','Help Text/Description']
- URL: Youtube playlist/title URL.
- PATH (optional): Path where this particular playlist/title will be saved. Provide absolute PATH here.

All custom arguments are visible in --help [`$ yt-audio --help`]

The default save PATH is **$HOME/Music**.  PATH can be configured by user in config file (OUTPUT_DIRECTORY = \<dir>). For playlists, one more directory of \<PlaylistName> is created where all playlist records are saved.

#### Keeping track of downloaded titles/playlists
yt-audio has an added feature of keeping track of audio files using **file's metadata**. This removes the requirement of additional archive file to store title(s) info (option provided by youtube-dl).

User can specify any of the two ways to keep track of downloaded titles. (By default, downloaded titles are **not tracked**)


_**Using File Metadata**_

To use file's metadata, pass `--use-metadata` argument to yt-audio. To use metadata everytime, you can set `USE_METADATA = 1` in config file. Metadata method requires following to work:
- `--add-metadata` argument to youtube-dl (`--add-metadata` argument is added by yt-audio by default. If you don't want this, you can re-configure youtube-dl command in config).


_Known limitations of using metadata method_
- I have tried this method with both MP3 and M4A format. MP3 works fine. M4a does not work.


**_Using Archive File_**

To use archive file method, pass `--use-archive` argument to yt-audio. To use archive file everytime with yt-audio, you can set `USE_ARCHIVE = 1` in config file. This will create 'records.txt' file in title's download location.

`--use-archive` flag simply passes youtube-dl's `--download-archive FILE` argument to youtube-dl. You can pass your own filename to youtube-dl as well with `--ytdl-args \"--download-archive FILE\"`. More info about ['--ytdl-args']() argument.

    # Enable metadata
    $ yt-audio --use-metadata [URL/custom_args]

    # Enable archive file - creates records.txt file
    $ yt-audio --use-archive [URL/custom_args]

    # Enable archive file - creates archive.txt file
    $ yt-audio --ytdl-args \"--download-archive FILE\" [URL/custom_args]


_If both metadata and archive file are enabled, archive file method is used_


#### Title/Playlist-specific PATH
User can also specify any arbitrary path for a particular playlist/title. This PATH can be specified as URL::PATH. If PATH is not provided, PATH from config file is used. If no path is present in config, **$HOME/Music** path is used

#### Changing output format
Downloaded file's output format can be specified with `--output-format` argument. [Output Template](https://github.com/ytdl-org/youtube-dl/blob/master/README.md#output-template). Default output format is `"%(title)s.%(ext)s"`

#### Passing additional paramaters to youtube-dl
yt-audio gives user the flexibility to pass additional parameters to youtube-dl directly from command-line. Additional arguments can be provided with `--ytdl-arguments` yt-audio argument. Arguments passed to `ytdl-arguments` are passed as-it-is to youtube-dl.

    $ yt-audio `--ytdl-args \"--download-archive FILE --user-agent UA\"`

**NOTE:** Make sure to escape double-quotes **"** when passing arguments to `--ytdl-args`. Else the arguments passed to `--ytdl-args` will be read as input arguments to yt-audio.

#### Modifying default youtube-dl/helper commands
The commands used by yt-audio can be modified from config file. Unusual parameters might break the program. If the parameter is legit and should have (ideally) worked but it didn't, please [raise an issue](https://github.com/pseudoroot/yt-audio/issues/new).

## Usage Examples

    # Synchronizes/downloads --custom1 and --custom2 custom argument URLs and download specified URL as well.
    $ yt-audio --custom1 --custom2 https://youtube.com/playlist?list=abcxyz

    # Saves playlist to /my/path/p1/<PlaylistName>/ and single audio to /some/another/path
    $ yt-audio https://youtube.com/playlist?list=abcxyz::/my/path/p1 https://www.youtube.com/watch?v=abcxyz::/some/another/path

    # Adding additional youtube-dl arguments
    # This will append additional arguments to youtube-dl download command
    $ yt-audio --ytdl-args \"arg1 arg2\" https:youtube.com/abc https://youtube.com/xyz::DIR

    # Different output format
    $ yt-audio --output-format "%(display_id)s.%(ext)s" https://youtube.com/...


## yt-audo defaults
The following commands are used by yt-audio to download and manage audio. The commands are configurable using config file.

**youtube-dl audio download**

    # (-x --print-json -o "$OUTPUT$" $URL$) are mandatory
    $ youtube-dl -x --print-json --audio-format mp3 --audio-quality 0 --add-metadata --embed-thumbnail -o "$OUTPUT$" $URL$

**get playlist/URL info**

    $ youtube-dl --flat-playlist -J $PLAYLIST_URL$

**get file's metadata** (used when downloaded titles are tracked using metadata)

    $ ffprobe -v quiet -print_format json -show_format -hide_banner "$PATH$"


## Limitations
- Keeping track of downloaded tracks works with youtube.com only (for now).

## Bugs/Issues
Please [create](https://github.com/pseudoroot/yt-audio/issues/new) issue for the same.
I'm open to suggestions as well :)

## Contact
Feel free get in touch with me via [Twitter](https://twitter.com/pseud0root) or [Email](mailto:pseudoroot@protonmail.ch).

# License
[MIT](https://github.com/pseudoroot/yt-audio/blob/master/LICENSE)
