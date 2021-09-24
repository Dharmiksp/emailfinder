from __future__ import print_function

import logging


def configure():
    # logging configuration
    logging.basicConfig(filename='myapp.log', filemode='w', format='%(asctime)s - %(levelname)s : %(message)s',
                        level='DEBUG')
    # replacing print to info
    print = logging.info
    return print