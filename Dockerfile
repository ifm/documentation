FROM ghcr.io/ifm/ifm3d:v1.3.3-ubuntu-amd64

RUN sudo apt update && sudo DEBIAN_FRONTEND=noninteractive apt-get install -y\
        build-essential \
        cmake \
        coreutils \
        git \
        jq


# c++ examples
WORKDIR /home/ifm
# Need to install a more recent version of nlhomann json
# than what is provided by apt, to use with the schema validator.
RUN git clone --branch v3.11.2 https://github.com/nlohmann/json.git && \
    cd json && \
    mkdir build && \
    cd build && \
    cmake -DCMAKE_INSTALL_PREFIX=/usr -DJSON_BuildTests=OFF .. && \ 
    make && \
    sudo make install 
    
RUN git clone https://github.com/pboettch/json-schema-validator.git && \
    cd json-schema-validator && \
    mkdir build && \
    cd build && \
    cmake -DCMAKE_INSTALL_PREFIX=/usr -DJSON_VALIDATOR_BUILD_TESTS=OFF -DJSON_VALIDATOR_BUILD_EXAMPLES=OFF .. && \
    make && \
    sudo make install 


COPY --chown=ifm . /home/ifm/examples
WORKDIR /home/ifm/examples/build
RUN cmake .. && cmake --build .

# python examples
WORKDIR /home/ifm/examples
RUN pip install -r requirements.txt
