FROM jupyter/tensorflow-notebook

USER root
COPY . ${HOME}
RUN chown -R ${NB_USER} ${HOME}

RUN apt-get update; \
    apt-get -y upgrade
RUN apt-get -y install cmake curl
RUN CMAKE_INSTALLER=install-cmake.sh && \
         curl -sSL https://cmake.org/files/v3.11/cmake-3.11.3-Linux-x86_64.sh -o ${CMAKE_INSTALLER} && \
        chmod +x ${CMAKE_INSTALLER} && \
         ./${CMAKE_INSTALLER} --prefix=/usr/local --skip-license
RUN alias cmake=/usr/local/bin/cmake
# RUN apt-get install -y python3 python3-pip python-pip
RUN apt-get install sudo
RUN pip install scipy pandas numpy matplotlib sklearn statsmodels nibabel plotly webcolors scikit-image wheel
RUN git clone https://github.com/ANTsX/ANTsPy.git
# RUN cd ANTsPy  && python3 setup.py  install
# RUN cd ANTsPy  && python3 setup.py bdist_wheel && cd ..
RUN wget https://github.com/ANTsX/ANTsPy/releases/download/v0.2.0/antspyx-0.2.0-cp37-cp37m-linux_x86_64.whl
RUN pip install antspyx-0.2.0-cp37-cp37m-linux_x86_64.whl
RUN chmod 755 *
RUN rm antspyx-*cp37-cp37m-linux_x86_64.whl install-cmake.sh
## Become normal user again
USER ${NB_USER}
