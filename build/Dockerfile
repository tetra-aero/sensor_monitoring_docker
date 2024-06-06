FROM ubuntu:latest
# use bash 
SHELL ["/bin/bash", "-c"]
WORKDIR /build

#using vim as editor from preferance
ARG EDITOR=vim

#import python dependancies, need only to write what you whant to install in the file below
COPY pip_req.txt pip_req.txt

# update apt, and install can dependancies and editor
# delete cache after that
RUN apt-get update && apt-get upgrade -y && \
	apt-get install -y \
	iproute2 can-utils $EDITOR python3 python3-pip && \
	pip --no-cache-dir install -r pip_req.txt && \
	rm -rf /var/lib/apt/lists/* && \
	apt-get autoremove -y && apt-get clean
# set default editor
RUN echo "export EDITOR=\"$EDITOR\"" >> ~/.bashrc
#setting current dir as /code_rep
WORKDIR /code_rep
# `python3 print_hello.py` will be run
CMD ["python3", "print_hello.py"]
