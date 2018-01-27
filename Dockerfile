FROM python:3
ADD market_sales_inp.py /
RUN pip3 install numpy 
RUN pip3 install pandas 
RUN pip3 install requests
RUN pip3 install lxml
RUN pip3 install beautifulsoup4
RUN pip3 install bokeh
