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
    install_requires=[
        "pydantic>=1.8.2",
    ],
    entry_points={"console_scripts": [
    ]}
)
