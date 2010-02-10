from TestBoa import *
from TestCaseHelper import *
import logging

#LOG_FILENAME = '/tmp/testlogging.out'
#logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)
#logging.basicConfig(level=logging.DEBUG)


def printhelp():
    print "Usage:"
    print "prog /res dir/ /run dir/ /spec/ /testid/"

class MyFactory:

    def constructTestCase(self, param, par):
        teca = OneTestCase(param, par)
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
    suiteparam = RunSuiteParam(factory, None, propfile, globresource, resource, rundir)
    try:
        runSuite(suiteparam, testspec, testid)
    except Exception, e:
        print e

