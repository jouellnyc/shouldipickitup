#!/home/john/anaconda3/bin/python3.7


import datetime
import logging

def app_system_logger(text,app_level):

    date     = str(datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
    logfile  = f"/tmp/app_{date}.log"
    loglevel = "INFO"
    logging.basicConfig(filename=logfile, level=loglevel, format =
    '%(levelname)s %(asctime)s %(module)s %(process)d %(message)s')
    if  app_level == "error":
        logging.error(text)
    elif app_level == "info":
        logging.info(text)
    elif app_level == "warning":
        logging.warning(text)
    elif app_level == "debug":
        logging.debug(text)

if __name__ == "__main__":
    app_system_logger("great","info")
