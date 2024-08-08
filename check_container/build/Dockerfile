FROM ubuntu:latest
# use bash 
SHELL ["/bin/bash", "-c"]
WORKDIR /build

#using vim as editor from preferance
ARG EDITOR=vim

# update apt, and install can dependancies and editor
# delete cache after that
RUN apt-get update && apt-get upgrade -y 
#libralies to run balena cli
RUN apt-get install -y \
	openssh-client
# libraries to build balena cli
RUN apt-get install -y \
	gcc make git

RUN git clone https://github.com/balena-io/balena-cli.git -b v18.2.34 --depth=1

#clean up
RUN rm -rf /build/balena-cli
RUN rm -rf /var/lib/apt/lists/* && \
	apt-get autoremove -y && apt-get clean
# set default editor
RUN echo "export EDITOR=\"$EDITOR\"" >> ~/.bashrc
#setting current dir as /code_rep
WORKDIR /
# `python3 code_rep/receive_can.py` will be run
CMD ["python3", "code_rep/receive_can.py"]
