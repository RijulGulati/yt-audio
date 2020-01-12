# yt-audio
A simple, cross-platform configurable youtube-dl wrapper for downloading and managing youtube audio.

## Installation
- Requires [Python3](https://www.python.org/downloads/) (>=3.5), [youtube-dl](https://github.com/ytdl-org/youtube-dl) and [ffmpeg](https://www.ffmpeg.org/) as dependencies.

yt-audio can be installed via [pip](pip_link_here). Arch Linux users can use [AUR](link) as well.

`$ [sudo] pip install --upgrade yt-audio`

## Description and Features
yt-audio is a command-line program that is used download and manage audio from youtube.com. It is a youtube-dl wrapper program, which means it uses youtube-dl as backend for downloading audio. yt-audio tries to make audio/playlist management easy for users. It is cross-platform (Windows/Linux/MacOS).

### Features
- Manage single as well as playlist audio(s).
- Configure/Setup your own command-line arguments for managing playlists (See [usage](link) below)
- Save every audio/playlist to a different directory (directory specified in argument).
- Option to keep track of already-downloaded playlist titles with or without archive file (youtube-dl uses archive file. yt-audio for now **does not** use archive file to keep track. Archive file option will be added in future releases).

## Usage
    usage: yt-audio [OPTIONS] REQUIRED_ARGS

    A simple youtube-dl wrapper for downloading and managing youtube audio

    Required Arguments (Any/all):
    URL[::DIR]            Video/Playlist URL with (optional) save directory [URL::dir]
    -e, --example1        Example playlist [Custom] # Custom argument generated from config
    --all                 All [Custom] Arguments

    Optional Arguments:
    -h, --help            show this help message and exit
    -v, --version         show version and exit
    --ffprobe-command [FFPROBE_COMMAND]
                            ffprobe command
    --output-format [OUTPUT_FORMAT]
                            File output format
    --playlist-info-command [PLAYLIST_INFO_COMMAND]
                            Fetch playlist info
    --download-command [DOWNLOAD_COMMAND]
                            youtube-dl audio download command

yt-audio requires either URL or any custom argument(s) (or both) as mandatory input(s).

#### Custom Arguments
yt-audio gives user the ability to setup their own custom arguments for managing/synchronizing audio/playlists. Custom arguments can be setup using yt-audio's *config.ini* configuration file.

> **NOTE: The user will have to copy the configuration file as it is not copied during installation.**

**Unix/Linux Users:**
The default config location is **$XDG_CONFIG_HOME/yt-audio/** directory. In case *$XDG_CONFIG_HOME* is not set, the file can be placed in **$HOME/.config/yt-audio/** directory.

**Windows Users:** The default config location is **C:\\Users\\\<user>\\.config\\yt-audio**

**Setting up custom arguments**

The config file *config.ini* has URL_LIST[] option where users can specify arguments with corresponding URL and (optional) save directory. It's format is as follows:

    URL_LIST = [
                    # "['-short_arg1','long_arg1','Help Text/Description']::URL::PATH"
                    # PATH here specifies output directory for that particular playlist
                    # PATH should be absoulte directory path
                    # URL: Complete youtube title/playlist URL
                    # These arguments are visible in --help

                    # "['-e','--example1','Example playlist']::URL::PATH",
               ]

URL_LIST takes comma-separated string values. Each string value is formed from 3 components:

- CLI Argument - Argument to register. It is written in form: ['-short_arg','--long_arg','Help Text/Description']
- URL: Youtube playlist/title URL.
- PATH (optional): Path where this particular playlist/title will be saved. Provide absolute PATH here.

The default save PATH is **$HOME/Music**.  PATH can be configured by user in config file (OUTPUT_DIRECTORY = \<dir>). For playlists, one more directory of \<PlaylistName> is created where all playlist records are saved.

#### Title/Playlist-specific PATH
User can also specify any arbitrary path for a particular playlist/title. This PATH can be specified as URL::PATH.

#### Changing output format
Downloaded file's output format can be specified with `--output-format` argument. [Output Template](https://github.com/ytdl-org/youtube-dl/blob/master/README.md#output-template). Default output format is `"%(title)s.%(ext)s"`

## Usage Examples

    # Synchronizes/downloads --custom1 and --custom2 custom argument URLs and downloads specified URL as well.
    $ yt-audio --custom1 --custom2 https://youtube.com/playlist?list=abcxyz

    # Saves playlist to /my/path/p1/<PlaylistName>/ and single audio to /some/another/path
    $ yt-audio https://youtube.com/playlist?list=abcxyz::/my/path/p1 https://www.youtube.com/watch?v=abcxyz::/some/another/path

    # Custom youtube-dl download command.
    # Note: Arguments -x --add-metadata --print-json "$OUTPUT$" $URL$ are mandatory.
    # --add-metadata dependency will be removed in future releases.
    $ yt-audio --download-command "youtube-dl -x --add-metadata --print-json [args] -o "$OUTPUT$" $URL$" https:youtube.com/ https://youtube.com/::DIR

    # Different output format
    $ yt-audio --output-format "%(display_id)s.%(ext)s" https://youtube.com/...

## Limitations
- Works for youtube.com only (for now).
- Does not support m4a format. I have tested with mp3 format and it works fine. yt-audio relies on file's metadata (purl tag to be specific) to keep track of downloaded records. m4a format does not have purl meta tag, so it does not work. The purl meta-tag dependecy will be removed in the **next release** (giving user option to use archive file for keeping track of downloaded records).

## Bugs/Issues
Please [create](https://github.com/pseudoroot/yt-audio/issues/new) issue for the same.

# License
[MIT](https://github.com/pseudoroot/yt-audio/blob/master/LICENSE)