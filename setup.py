import setuptools

with open("README.md", "r", encoding = "utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name = "celery-ai",
    version = "1.0",
    author = "ortegaalfredo",
    author_email = "ortegaalfredo@gmail.com",
    description = "OpenAI keyboard integration",
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
