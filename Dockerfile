FROM rocker/binder:3.5.0

USER root
COPY . ${HOME}
COPY --chown=rstudio:rstudio . ${HOME}
RUN chown -R ${NB_USER} ${HOME}


COPY . /usr/local/src/scripts
COPY ./scripts/* /usr/local/src/scripts
WORKDIR /usr/local/src/scripts
RUN apt-get update; \
    apt-get -y upgrade
RUN apt-get -y install cmake   libssl-dev
RUN apt-get install -qqy x11-apps
RUN apt-get install -y vim nano zsh curl git sudo
RUN apt-get install -y x11vnc xvfb sudo libv8-dev

## Run an install.R script, if it exists.
RUN if [ -f install.R ]; then R --quiet -f install.R; fi
RUN apt-get python3.5 python3-pip python3-setuptools python3-dev

RUN pip3 install scipy pandas numpy matplotlib sklearn statsmodels nibabel
RUN pip3 install coveralls plotly webcolors scikit-image
RUN pip3 install keras
RUN git clone https://github.com/ANTsX/ANTsPy.git && cd ANTsPy  && python3 setup.py  install
