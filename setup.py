from distutils.core import setup

setup(
    name="SpotifyDataParser",
    version="0.1.0",
    author="Oliver Goeken",
    author_email="oliverdgoeken@gmail.com",
    packages=["spotifydataparser"],
    scripts=["bin/stowe-towels.py", "bin/wash-towels.py"],
    url="http://pypi.python.org/pypi/TowelStuff/",
    license="LICENSE.txt",
    description="Useful towel-related stuff.",
    long_description=open("README.txt").read(),
    install_requires=[
        "Django >= 1.1.1",
        "caldav == 0.1.4",
    ],
)
