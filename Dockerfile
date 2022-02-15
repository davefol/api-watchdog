# leverage the renci python base image
FROM renciorg/renci-python-image:v0.0.1

# switch to the new user created in the above image
USER nru

# set up working directory
WORKDIR /app

# Install dependencies
ADD setup.py VERSION README.md ./
RUN python setup.py egg_info && pip install `grep -v '^\[' *.egg-info/requires.txt`

# Add the rest of the code and install package
ADD . .

# add it a legit set of test files. good for manual testing
#ADD ./all_tests ./test

RUN pip install .[TRAPI]

