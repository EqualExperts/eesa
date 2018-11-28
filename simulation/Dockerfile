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
RUN echo "cd ~/ardupilot/ArduPlane; rm -f mav.* eeprom.bin; ~/ardupilot/Tools/autotest/sim_eesa.py --out 127.0.0.1:9000 --console -L ICEL --daemon 2>&1" > /root/sim_eesa.sh
RUN chmod a+x /root/sim_eesa.sh
EXPOSE 5503:5503/udp
EXPOSE 5760:5760/udp
EXPOSE 9000:9000/udp
ENTRYPOINT /root/sim_eesa.sh
