import unittest
import logging
import bg_scraper as bgs
import requests
import re

TESTCASE = "GLOBAL"

class ContextFilter(logging.Filter):
    """
    This is a filter which injects contextual information into the log.
    """
    def filter(self, record):
        record.TESTCASE = TESTCASE
        return True

class SimpleScraper(unittest.TestCase):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    f_handler = logging.FileHandler("{}-SimpleScraper.log".format(__name__))
    formatter = logging.Formatter("%(name)s::%(TESTCASE)s::%(levelname)s::%(message)s")
    f_handler.setFormatter(formatter)
    logger.addHandler(f_handler)
    
    
    def test_scraper_init(self):
        global TESTCASE
        validURL = "http://www.google.com/"
        invalidURL = "fake"
        unreachableURL = "http://127.0.0.2:5000/"


        TESTCASE = "test_scraper_init"
        self.logger.addFilter(ContextFilter())
        self.logger.info("Initialize logger to http://www.google.com/")
        bgs.SimpleScraper(validURL)
        self.logger.info("Succesfully initialize")


        self.logger.info("Initialize logger to invalid URL: {}".format(invalidURL))
        with self.assertRaises(requests.exceptions.MissingSchema) as cm:
            bgs.SimpleScraper(invalidURL)
        self.logger.debug("Raises message: {}".format(str(cm.exception)))
        if str(cm.exception) == "Invalid URL 'fake': No scheme supplied. Perhaps you meant https://fake?":
            self.logger.debug("Raises correct exception.")
        else:
            self.logger.error("Raises incorrect exception.")
        self.assertEqual(str(cm.exception), "Invalid URL 'fake': No scheme supplied. Perhaps you meant https://fake?")

        regex_mess = "Max retries exceeded with url: / \(Caused by NewConnectionError\('<urllib3.connection.HTTPConnection object at 0x[0-9a-f]+>: Failed to establish a new connection"
        self.logger.info("Initialize logger to unreachable URL: {}".format(unreachableURL))
        with self.assertRaises(requests.exceptions.ConnectionError) as cm:
            bgs.SimpleScraper(unreachableURL)
        self.logger.debug("Raises message: {}".format(str(cm.exception)))
        mess = str(cm.exception)
        match_ = re.search(regex_mess, mess)
        if match_:
            self.logger.debug("Raises correct exception.")
        else:
            self.logger.error("Raises incorrect exception.")
        self.assertTrue(str(cm.exception) != None)

        self.logger.info("Test done!")
        