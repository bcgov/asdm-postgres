import os
import logging

log = logging.getLogger(__name__)

def Log(level, outFile):

    logging.basicConfig(level=level,
                        format='%(message)s')

    if (outFile):
        f_handler = logging.FileHandler(outFile)
        f_handler.setLevel(logging.INFO)
        f_format = logging.Formatter('%(message)s')
        f_handler.setFormatter(f_format)
        log.addHandler(f_handler)

    return log