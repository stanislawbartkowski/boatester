import os.path
from TestBoa import *
from TestCaseHelper import *
import logging

#LOG_FILENAME = '/tmp/testlogging.out'
#logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)
logging.basicConfig(level=logging.DEBUG)
#logging.basicConfig(level=logging.INFO)


def printhelp():
    print "Usage:"
    print "prog /res dir/ /run dir/ /spec/ /testid/"

class ReportTestCase(unittest.TestCase):

    def __init__(self, param, teparam):
        unittest.TestCase.__init__(self, 'runTest')
        self.param = param
        self.teparam = teparam

    def setUp(self):
        prepareRunDir(self.param, self.teparam)

    def runTest(self):
        runcommand = self.teparam.getPar('runcommand')
        TestCaseHelper.copyFile(self.param, self.teparam, runcommand)

        testDir = self.param.getRunDir()
        pathcommand = os.path.join(testDir,runcommand)
        TestCaseHelper.prepareRunCommand(pathcommand)

        res = runBin(self.param, pathcommand, runcommand)
        self.assertEqual(0,res)
        res = compareFiles(self.param, self.teparam, "out", ".lst", "out")
        self.assertTrue(res)



class MyFactory:

    def constructTestCase(self, param, tepar):
        runcommand = tepar.getPar('runcommand')
        if runcommand == None : return None
        teca = ReportTestCase(param, tepar)
        return [teca]


if __name__ == "__main__":
    if len(sys.argv) != 5:
        printhelp()
        sys.exit(4)
    resource = sys.argv[1]
    rundir = sys.argv[2]
    testspec = sys.argv[3]
    testid = sys.argv[4]
    globresource = resource
    propfile = None
    factory = TestCaseFactory()
    factory.register(MyFactory())
    suiteparam = RunSuiteParam(factory, None, propfile, globresource, resource, rundir)
    try:
        runSuite(suiteparam, testspec, testid)
    except Exception, e:
        print e

