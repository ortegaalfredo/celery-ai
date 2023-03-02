import setuptools,os

with open("README.md", "r", encoding = "utf-8") as fh:
    long_description = fh.read()

lib_folder = os.path.dirname(os.path.realpath(__file__))
requirement_path = lib_folder + '/requirements.txt'
install_requires = []
if os.path.isfile(requirement_path):
    with open(requirement_path) as f:
        install_requires = f.read().splitlines()

setuptools.setup(
    name = "celery-ai",
    version = "1.11",
    author = "ortegaalfredo",
    author_email = "ortegaalfredo@gmail.com",
    description = "OpenAI keyboard integration",
    install_requires = install_requires,
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://github.com/ortegaalfredo/celery-ai",
    project_urls = {
        "Bug Tracker": "https://github.com/ortegaalfredo/celery-ai/issues",
    },
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    scripts=['src/celery-ai.py'],
    package_dir = {"": "src"},
    packages = setuptools.find_packages(where="src"),
    python_requires = ">=3.6"
)
