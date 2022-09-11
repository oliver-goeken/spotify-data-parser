from distutils.core import setup

setup(
    name="SpotifyDataParser",
    version="0.1.0",
    author="Oliver Goeken",
    packages=["spotifydataparser"],
    url="https://github.com/oliver-goeken/spotify-data-parser",
    license="LICENSE.txt",
    description="Basic spotify listening data parsing.",
    long_description=open("README.txt").read(),
    install_requires=open("requirements.txt").read(),
)
