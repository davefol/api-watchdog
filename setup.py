from setuptools import setup, find_packages

def readme():
    with open("README.md") as f:
        return f.read()

def version():
    with open("VERSION") as f:
        return f.read()

setup(
    name="api_watchdog",
    version=version(),
    packages = find_packages(),
    license="MIT",
    authot="David Folarin",
    description="API watchdog",
    long_description=readme(),
    long_description_content_type="text/markdown",
    install_requires=[
        "pydantic>=1.8.2",
    ],
    extras_require={
        "TRAPI": ["reasoner-pydantic"]
    },
    entry_points={"console_scripts": [
    ]}
)
