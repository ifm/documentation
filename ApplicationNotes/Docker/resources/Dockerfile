#arm64v8 is the pre-requisite for running the container on the VPU.
FROM arm64v8/python:3.9.6-slim-buster as compile-image

#Security updates
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get -y update && apt-get -y upgrade

#For h5py, you need several libs and to install it from source (because of the architecture)
#https://docs.h5py.org/en/stable/build.html#source-installation
RUN apt-get -y install --no-install-recommends build-essential \
    gcc \
    python-dev \
    software-properties-common \
    libhdf5-dev \
    pkg-config

#Create a virtual env for a multistage build.
#h5py needs gcc etc. to compile. This increases the image size. Using the venv
#can decrease the final image size.
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

#Install(Update) python packages and dependencies separate from ifm3dTiny - improves Docker caching etc.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

#Use a build image for the smaller size
FROM arm64v8/python:3.9.6-slim-buster as build-image

#Install libhdf5 for h5py
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get -y update && apt-get -y upgrade
RUN apt-get -y install --no-install-recommends libhdf5-103 && apt-get clean

#Copy the venv from the compile image and activate it
COPY --from=compile-image /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

#Install latest ifm3dTiny version
RUN pip install --no-cache-dir ifmO3r==0.1.3

#Due to security reasons, using a "user" is recommended
RUN useradd --create-home pythonuser
USER pythonuser

#Easier to debug the container
ENV PYTHONFAULTHANDLER=1

#Start the repl (docker run -it) and import the ifm3dTiny directly
ENTRYPOINT [ "python3.9", "-i", "-c", "import ifmO3r.ifm3dTiny" ]