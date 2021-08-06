import logging

logger_app = logging.getLogger("app")
logger_data = logging.getLogger("data")

class LOGGER:

    def __init__(self, name):
        self.logger = logging.getLogger(name)

    def sethandler(self, logfile):
        self.c_handler = logging.StreamHandler()
        self.f_handler = logging.FileHandler(logfile)
        self.c_handler.setLevel(logging.INFO)
        self.f_handler.setLevel(logging.INFO)
        c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
        f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.c_handler.setFormatter(c_format)
        self.f_handler.setFormatter(f_format)
        self.logger.addHandler(self.c_handler)
        self.logger.addHandler(self.f_handler)






