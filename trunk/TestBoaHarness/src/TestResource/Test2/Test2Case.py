import unittest
import Test2Case
import TestCaseHelper

def injectParam(param,tepar) :
    Test2Case.param = param
    Test2Case.tepar = tepar

class TestSuite(unittest.TestCase):

    def setUp(self):
       print "setUp"
       TestCaseHelper.prepareRunDir(Test2Case.param, Test2Case.tepar)

    def testCase1(self):
        print "testCase1"

    def testCase2(self):
        print Test2Case.tepar.getDescr()
        print "testCase2"

