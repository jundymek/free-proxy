import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
    name='free_proxy',
    version='1.2.0',
    author="jundymek",
    author_email="jundymek@gmail.com",
    description="Proxy scraper for further use",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jundymek/free-proxy",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    install_requires=['lxml>=5.0,<7', 'requests>=2.31,<3']
)
