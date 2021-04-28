# Set the base image to Ubuntu

FROM selenium/standalone-chrome-debug

# Necessary for HEADLESS
#RUN sudo Xvfb :10 -ac &
#ENV DISPLAY=:10

RUN sudo apt-get update && \
 sudo apt-get install -y tar git curl nano wget dialog net-tools build-essential && \
 sudo apt-get install -y python python-dev python-distribute python-pip && \
 sudo locale-gen --purge en_US.UTF-8

ADD . /home/seluser/testaframe

RUN pip3 install -r /home/seluser/testaframe/pip_requirements.txt && \
 sudo ln -s /home/seluser/.local/bin/nosetests /usr/local/bin/nosetests

WORKDIR /home/seluser/testaframe
