try:
    from setuptools import setup, find_namespace_packages
except ModuleNotFoundError as ex:
    print(ex.msg)
    exit(1)

from yt_audio.version import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="yt-audio",
    version=__version__,
    author="pseudoroot",
    author_email="pseudoroot@protonmail.ch",
    description="A simple, configurable youtube-dl wrapper to download and manage youtube audio (with added features)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pseudoroot/yt-audio",
    packages=find_namespace_packages(),
    install_requires=['youtube-dl'],
    entry_points={
        'console_scripts': [
            'yt-audio = yt_audio.YTAudio:main'
        ]
    },
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Topic :: Multimedia :: Sound/Audio",
        "License :: OSI Approved :: MIT License"
    ],
    license='MIT',
    python_requires='>=3.5',
)
