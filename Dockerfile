FROM ubuntu:latest
# use bash 
SHELL ["/bin/bash", "-c"]
WORKDIR /build

#using vim as editor from preferance
ARG EDITOR=vim

# update apt, and install can dependancies and editor
# delete cache after that
RUN apt-get update && apt-get upgrade -y && \
	apt-get install -y \
	iproute2 can-utils $EDITOR python3 python3-can && \
	rm -rf /var/lib/apt/lists/* && \
	apt-get autoremove -y && apt-get clean
COPY code_rep /code_rep
RUN mkdir /log
# set default editor
RUN echo "export EDITOR=\"$EDITOR\"" >> ~/.bashrc
#setting current dir as /code_rep
WORKDIR /
# `python3 code_rep/receive_can.py` will be run
CMD ["python3", "code_rep/receive_can.py"]
