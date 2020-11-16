# set base image (host OS)
FROM python:3.9.0-slim

# set the working directory in the container
WORKDIR /code

# copy the content of the local src directory to the working directory
COPY app/ .

EXPOSE 5000/tcp
EXPOSE 5000/udp

# command to run on container start
CMD [ "python", "./simple-servicetag-generator.py" ] 