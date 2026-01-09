import unittest
import os
from main import *

if __name__ == "__main__":
    if os.path.exists('test111.png'):
        os.remove("test111.png")
    suite = unittest.TestSuite()
    suite.addTest(th_lang_detect('test_04_references_menu'))
    suite.addTest(th_lang_detect('test_08_modules'))

    runner = unittest.TextTestRunner()
    runner.run(suite)

