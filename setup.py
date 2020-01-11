try:
    import setuptools
except ModuleNotFoundError as ex:
    print(ex.msg)
    exit(1)

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="yt-audio-pseudoroot",
    version="0.1",
    author="pseudoroot",
    author_email="pseudoroot@protonmail.ch",
    description="A simple, configurable youtube-dl wrapper to download and manage youtube audio.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pseudoroot/yt-audio",
    packages=setuptools.find_packages(),
    install_requires=['youtube-dl'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Topic :: Multimedia :: Sound/Audio"
    ],
    python_requires='>=3.5',
)
