# print sys.path
from TestBoa import *
from NZPDATestCase import *
import logging

#LOG_FILENAME = '/tmp/testlogging.out'
#logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)
logging.basicConfig(level=logging.DEBUG)
#logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    if len(sys.argv) != 5:
        printhelp()
        sys.exit(4)
    resource = sys.argv[1]
    rundir = sys.argv[2]
    testspec = sys.argv[3]
    testid = sys.argv[4]
    globresource = resource + "/resource"
    propfile = globresource + "/commonprop.cfg"
    factory = TestCaseFactory()
    factory.register(NZPDAFactory())
    suiteparam = RunSuiteParam(factory, None, propfile, globresource, globresource+"/test", rundir)
    try:
        runSuite(suiteparam, testspec, testid)
    except Exception, e:
        print e

