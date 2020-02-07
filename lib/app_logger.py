#!/usr/bin/env python3

import datetime
import logging

class AppLog:

    app       =  "shouldipickitup"

    def app_system_logger(self, text, app_level):

        self.date      = str(datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
        self.app_level = app_level
        self.text      = text
        self.logfile   = f"/tmp/{self.app}_{self.date}.log"

        logging.basicConfig(filename=self.logfile, format =
            '%(levelname)s %(asctime)s %(module)s %(process)d %(message)s')
        if  app_level == "error":
            logging.error(text)
        elif app_level == "info":
            logging.info(text)
        elif app_level == "warning":
            logging.warning(text)
        elif app_level == "debug":
            logging.debug(text)
        elif app_level == "exception":
            logging.exception(text)
        else:
            logging.info(text)

if __name__ == "__main__":
    mylog = AppLog()
    mylog.app_system_logger("great","info")
