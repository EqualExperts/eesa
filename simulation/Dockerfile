FROM ubuntu:18.10
LABEL maintainer="tsquires@equalexperts.com"
RUN apt-get update
RUN apt-get -y install python 
RUN apt-get -y install python-pip 
RUN apt-get -y install git 
RUN pip install dronekit
RUN pip install MAVProxy
RUN cd ~; git clone https://github.com/ArduPilot/ardupilot.git; cd ardupilot; git submodule update --init --recursive
RUN cd ~/ardupilot; Tools/scripts/install-prereqs-ubuntu.sh -y; . ~/.profile
RUN echo "ICEL=64.073,-19.754,10000,180" >> ~/ardupilot/Tools/autotest/locations.txt
ADD sim_eesa.py /root/ardupilot/Tools/autotest/sim_eesa.py
RUN chmod a+x /root/ardupilot/Tools/autotest/sim_eesa.py
WORKDIR /root/ardupilot/ArduPlane
EXPOSE 9000:9000/udp
ENTRYPOINT ["/root/ardupilot/Tools/autotest/sim_eesa.py", "--out", "docker.for.mac.localhost:9000", "--daemon"]
CMD ["-L", "ICEL"]
