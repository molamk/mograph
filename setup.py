import pathlib
from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).parent

README = (HERE / "README.rst").read_text()

print(README)

setup(
    name="mograph",
    version="0.1.5",
    description="A Dependency Graph Manager",
    long_description=README,
    long_description_content_type="text/x-rst",
    author="Mohamed Lamouchi",
    author_email="molamk@protonmail.com",
    url="https://github.com/molamk/mograph",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=find_packages(exclude=("tests", "docs")),
    include_package_data=True,
    install_requires=["click", "pyyaml", "coloredlogs", "pytest"],
    entry_points={"console_scripts": ["mograph=mograph.__main__:main"]},
)
