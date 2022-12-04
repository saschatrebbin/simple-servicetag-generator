# set base image (host OS)
FROM python:3.9.0-slim

# set the working directory in the container
WORKDIR /code

# copy the content of the local src directory to the working directory
COPY app/requirements.txt .

# copy the content of the local src directory to the working directory
#COPY app/bottle.py .

# copy the content of the local src directory to the working directory
COPY app/simple-servicetag-generator.py .

# install dependencies
RUN pip3 install -r requirements.txt

# command to run on container start
CMD [ "python", "./simple-servicetag-generator.py" ] 