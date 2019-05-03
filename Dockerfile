FROM jupyter/tensorflow-notebook

USER root
COPY . ${HOME}
RUN chown -R ${NB_USER} ${HOME}

# RUN CMAKE_INSTALLER=install-cmake.sh && \
#         curl -sSL https://cmake.org/files/v3.11/cmake-3.11.3-Linux-x86_64.sh -o ${CMAKE_INSTALLER} && \
#        chmod +x ${CMAKE_INSTALLER} && \
#         ./${CMAKE_INSTALLER} --prefix=/usr/local --skip-license
# RUN alias cmake=/usr/local/bin/cmake
# RUN apt-get install -y python3 python3-pip python-pip
#	RUN chown -R ${NB_USER} /home/rstudio/.cache/pip/http
#	RUN chown -R ${NB_USER} /home/rstudio/.cache/pip
RUN apt-get install sudo
RUN pip install scipy pandas numpy matplotlib sklearn statsmodels nibabel
RUN pip install plotly webcolors scikit-image
RUN pip install wheel
RUN git clone https://github.com/ANTsX/ANTsPy.git 
RUN cd ANTsPy  && python3 setup.py  install
RUN python3 setup.py bdist_wheel && cd ..
# RUN wget https://github.com/ANTsX/ANTsPy/releases/download/v0.1.8/antspyx-0.1.7-cp35-cp35m-linux_x86_64.whl
# RUN pip install --user antspyx-0.1.7-cp35-cp35m-linux_x86_64.whl
# RUN chmod 755 *
# RUN wget https://github.com/ANTsX/ANTsPy/releases/download/v0.1.8/antspy-0.1.7-cp36-cp36m-linux_x86_64.whl
# RUN sudo -H pip install antspy-0.1.7-cp36-cp36m-linux_x86_64.whl
## Become normal user again
USER ${NB_USER}

