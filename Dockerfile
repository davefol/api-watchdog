# leverage the renci python base image
FROM renciorg/renci-python-image:v0.0.1

# set up working directory
WORKDIR /app

# Install dependencies
ADD requirements-lock.txt .
RUN pip install -r requirements-lock.txt

# Add the rest of the code and install package
ADD . .

# add it a legit set of test files. good for manual testing
#ADD ./all_tests ./test

RUN pip install .

# switch to the new user created in the above image
USER nru
