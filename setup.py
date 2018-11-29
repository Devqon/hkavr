import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="hkavr",
    version="0.0.5",
    author="Sander Geerts",
    author_email="s.geerts@live.nl",
    description="Library for controlling a Harman Kardon AVR",
    long_description="Library for controlling a Harman Kardon AVR",
    url="https://github.com/Devqon/hkavr",
    license="MIT",
    install_requires=["requests"],
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)