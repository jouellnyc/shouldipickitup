FROM python:3
RUN apt-get update -y &&  apt-get install
RUN pip install --upgrade pip
RUN mkdir /shouldipickitup
COPY . /shouldipickitup
WORKDIR /shouldipickitup
RUN pip install -r requirements.txt
EXPOSE 5001
CMD /usr/local/bin/gunicorn  -w 4 app:app
