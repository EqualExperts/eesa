FROM ubuntu:18.10
LABEL maintainer="tsquires@equalexperts.com"
ENV TINI_VERSION v0.18.0
ENV LOCATION ICEL
ENV UPD_HOST docker.for.mac.localhost
ENV START_ALTITUDE 30000
RUN apt-get update
RUN apt-get -y install python 
RUN apt-get -y install python-pip 
RUN apt-get -y install git 
RUN apt-get -y autoremove
RUN apt-get -y clean
RUN pip install MAVProxy
RUN cd ~; git clone https://github.com/ArduPilot/ardupilot.git; cd ardupilot; git submodule update --init --recursive
RUN cd ~/ardupilot; Tools/scripts/install-prereqs-ubuntu.sh -y; . ~/.profile
ADD locations.txt /root/ardupilot/Tools/autotest/locations.txt
ADD sim_eesa.py /root/ardupilot/Tools/autotest/sim_eesa.py
RUN chmod a+x /root/ardupilot/Tools/autotest/sim_eesa.py
ADD sitl_alt.patch /root/ardupilot/sitl_alt.patch
RUN cd /root/ardupilot; git apply sitl_alt.patch
WORKDIR /root/ardupilot/ArduPlane
EXPOSE 9000:9000/udp
EXPOSE 5503:5503/udp
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini
ENTRYPOINT ["/tini", "--", "/root/ardupilot/Tools/autotest/sim_eesa.py", "--out", "docker.for.mac.localhost:9000", "--daemon"]
CMD ["-L", "ICEL"]
