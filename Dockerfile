FROM python:3.5
RUN CMAKE_INSTALLER=install-cmake.sh && \
        curl -sSL https://cmake.org/files/v3.11/cmake-3.11.3-Linux-x86_64.sh -o ${CMAKE_INSTALLER} && \
        chmod +x ${CMAKE_INSTALLER} && \
         ./${CMAKE_INSTALLER} --prefix=/usr/local --skip-license
RUN alias cmake=/usr/local/bin/cmake
RUN pip3 install scipy pandas numpy matplotlib sklearn statsmodels nibabel
RUN pip3 install coveralls plotly webcolors scikit-image
RUN pip3 install keras tensorflow
# RUN git clone https://github.com/ANTsX/ANTsPy.git && cd ANTsPy  && python3 setup.py  install
RUN wget https://github.com/ANTsX/ANTsPy/releases/download/v0.1.8/antspyx-0.1.7-cp35-cp35m-linux_x86_64.whl
RUN sudo -H pip3 install antspyx-0.1.7-cp35-cp35m-linux_x86_64.whl -t .
RUN sudo -H pip3 install --user antspyx-0.1.7-cp35-cp35m-linux_x86_64.whl
