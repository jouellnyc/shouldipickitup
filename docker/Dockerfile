FROM python:3
RUN pip3 install --upgrade pip
RUN pip3 install numpy 
RUN pip3 install pandas 
RUN pip3 install requests
RUN pip3 install lxml
RUN pip3 install beautifulsoup4
RUN pip3 install bokeh
RUN groupadd -g 999 appuser && useradd -r -u 999 -g appuser appuser && mkdir /data && chown appuser.appuser /data
USER appuser
ADD --chown=appuser:appuser  market_sales.py /
