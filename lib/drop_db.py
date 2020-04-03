#!/usr/bin/env python3

import mongodb
import logging 

if __name__ == "__main__":

    try:
        mg = mongodb.MongoCli()
        drop = mg.drop_db()
        if drop is None:
            print("DB dropped OK")
    except Exception as e:
        logging.exception(e)


