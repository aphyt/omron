import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="omron",
    version="0.1.6",
    author="Joseph Ryan",
    author_email="jr@aphyt.com",
    description="A library to communicate with Omron devices",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://aphyt.com",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src")
)
