FROM python:3.9

# set up working directory
WORKDIR /app

# Install dependencies
ADD setup.py VERSION README.md .
RUN python setup.py egg_info && pip install `grep -v '^\[' *.egg-info/requires.txt`

# Add the rest of the code and install package
ADD . .
RUN pip install .[TRAPI]