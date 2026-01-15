import logging
import sys
import unittest

from test_langs import *
from function import *
from main import baselangdetect





logger = logging_init(f'result/result_{now_str}/logging.log')
sys.stdout = PrintToLogger(logger)
sys.stderr = PrintToLogger(logger, level=logging.ERROR)

suite = unittest.TestSuite()
loader = unittest.TestLoader()

#清空测试结果.csv内容
test_case_list=[Test_Th_LangDetect,Test_ar_LangDetect,Test_ind_LangDetect,Test_es_LangDetect,Test_ptbr_LangDetect,Test_vn_LangDetect]
test=[Test_vn_LangDetect]

for i in test_case_list:
# for i in test:
    suite.addTest(loader.loadTestsFromTestCase(i))
runner = unittest.TextTestRunner()
result = runner.run(suite)

# 所有测试完成后，关闭共享的 browser 和 playwright
if baselangdetect._browser_instance:
    baselangdetect._browser_instance.close()
if baselangdetect._playwright_instance:
    baselangdetect._playwright_instance.stop()