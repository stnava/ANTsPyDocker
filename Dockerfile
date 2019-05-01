FROM python:3.6

RUN pip3 install scipy pandas numpy matplotlib sklearn statsmodels nibabel
RUN pip3 install coveralls plotly webcolors scikit-image;
RUN wget https://github.com/ANTsX/ANTsPy/releases/download/v0.1.8/antspy-0.1.7-cp36-cp36m-linux_x86_64.whl
RUN pip3 install antspy-0.1.7-cp36-cp36m-linux_x86_64.whl
CMD ["/init"]
