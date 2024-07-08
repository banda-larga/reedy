from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="reedy",
    version="0.1.0",
    author="Edoardo Federici",
    author_email="edoardo.federici@outlook.com",
    description="A package to convert HTML to Markdown",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/banda-larga/reedy",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[
        "trafilatura",
        "beautifulsoup4",
        "parsel",
    ],
)
