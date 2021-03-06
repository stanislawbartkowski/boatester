#
# Copyright [2016] the stanislaw.bartkowski@gmail.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Some public helper functions and classes for Boa test harness
"""

__authors__ = [
    '"Stansislaw Bartkowski" <stanislawbartkowski@gmail.com>',
]

import logging
import filecmp
import os
import shutil
import tempfile
import time
import unittest

def exist(fname):
    """ Check if directory exists (as expected)
    
    Args:
      fname : directory, path name, to test
      
    Returns:
      Nothing
      
    Raise:
      TestException if directory not exist
    """

    if not os.path.exists(fname):
        raise TestException(fname + " file does not exists")

def _getKey(cf, key):
     if cf == None : return None
     ikey = osPrefix() + "." + key
     if cf.has_key(ikey): return cf[ikey]
     if cf.has_key(key): return cf[key]
     return None

def getParam(param, teparam,key, default=None) :
     """"Returns parameter from global and local properties file
     Args:
        param : global configuration file
        teparam: local, test confoguration file
        key : key value
        default: if None then error is raised if parameter does not exist
                      otherwise default parameter is returned
     Returns:
        Parameter value. Firstly local configuraiton is scanned then global if not found
     """
     
     val = teparam.getPar(key)
     if val : return val
     val = param.getPar(key)
     if val : return val
     # check environment
     if os.environ.has_key(key) :
        return os.environ[key]
     if default == None :
         raise TestException(key + " parameter not found. Cannot continue.")
     return default

def getResourceDirPath(teparam,param,path) :
      id = teparam.getTestId()
      teDir = param.getTestDir(id)  
      return os.path.join(teDir, path)
     
def osPrefix():
    """Returns system prefix

  Args:
    No args

  Returns:
    linux/windows

  Raises:
    Nothing
    """
    name = os.name
    if name == "posix": return "linux"
    return "windows"

def isLinux():
    """Is host system linux

  Args:
    No args

  Returns:
    True: linux, False: windows

  Raises:
    Nothing
    """
    prefix = osPrefix()
    if prefix == "linux": return True
    return False
    
def prepareRunCommand(command):
    """Modify command (binary file) with 'executable' access
    
    Is valid for windows but do nothing
    On linux: chmod a+x,g+a,u+x command

  Args:
    File name

  Returns:
    Nothing

  Raises:
    Exception if error
    """
    if not isLinux(): return
    os.chmod(command, 0777)

def getTmpName(tempdir=None):
    """Returns temporary and uniq file name

  Args:
    Nothing

  Returns:
    File name

  Raises:
    Exception if error
    """
    if tempdir == None: f = tempfile.mkstemp()
    else: f = f = tempfile.mkstemp(dir=tempdir)
    tmp = f[1]
    os.close(f[0])
    return tmp


def __waitforBin(bin):
    """Stops until process is not visible in ps command.

    Wait for command to exit

  Args:
    Command to watch

  Returns:
    Nothing

  Raises:
    Nothing
    """
    if not isLinux() : return
    while True:
        time.sleep(1)
        tmp = getTmpName()
        logging.debug("Wait for " + bin)
        logging.debug("Read ps output to temp " + tmp)
        os.system("ps -aef >" + tmp)
        f = open(tmp)
        li = f.readlines()
        f.close()
        os.unlink(tmp)
        found = 0
        for l in li:
            logging.debug(l)
            if l.find(bin) != -1:
                found = 1
                break
        if not found:
            break

class ChangeDir :
    """ Change current directory and keeps previous

    Attributes:
      param : TestParam container
      dir : previous directory
    """

    def __init__(self,param) :
        """ Constructor

        Args:
          param : TestParam container
        """
        self.__param = param
        self.__dir = os.getcwd()
        os.chdir(param.getRunDir())

    def restore(self) :
        """ Restores previous directory
        """
        os.chdir(self.__dir)
        

def runBin(param, com, binarywaited=None,bash=False):
    """Launch command and wait for exit


  Args:
    param: TestParam
    com: command to lauch
    binarywaited: if not none then wait for binary string visible in ps command 

  Returns:
    Exit code

  Raises:
    Exception if any error has occured
    """
    d = ChangeDir(param)
    # os.system calls /bin/sh which does not recognized source command properly
    if isLinux() and bash : res = os.system("/bin/bash " + com)
    else : res = os.system(com)
    logging.debug(com)
    if binarywaited != None : __waitforBin(binarywaited)
    d.restore()
    return res

    """Replace variables using format (like ConfigParser) %(..)s
    
    Args:
      line : line to be changed
      p : lamba function which return the value for parameter
      
    Returns:
      Fixed line
      
    Raises: 
      Exception if variable for replacement not found
      
    """

def replaceLine(line,  p):
    while 1 :
        low = line.rfind("%(")
        if low == -1 : break
        up = line.rfind(")s")
        if up == -1 : break
        before = line[0: low]
        after = line[up+2: len(line)]
        key = line[low+2: up]
        value = p(key)
        if value == None : 
	    raise TestException(key + " variable for replacement not found !")
        line = before + value + after
        
    return line               

def readListOfLinesWithReplace(fName,  p) :
     """ Read list of lines from file with variable substitution
     Args:
       fName file name (must exists)
       p lambda function which return value for variable
     
     Returns:
      List of lines read
     """
     f = open(fName, "r")
     list = f.readlines()
     f.close()
     lines = []
     for l in list :
         lines.append(replaceLine(l, p))
     return lines        



class TestException(Exception):

    """General exception raised

      Attributes:
       s : error message

    """

    def __init__(self, s):
        """Constructor

        Args:
          s : error message
        """
        self.s = s
        logging.critical(s)

    def draw(self):
        """Prints error message

        Args: nothing

        Returns: nothing

        Raises: nothing

        """
        print self.s

    def __str__(self) :
        return self.s


class OneTestParam:

    """Container for test case parameters

     Attributes:
       testId : string, test identifier
       cf : dictionary, test properties, key : value
         predefined:
          'descr' - short test description
          'testcase' : if not None predefined python test case
          'copytestres' : if not Nodn test resource to copy
          'copycommonres' : if not None common resource to copy
          'command' : if not None predefined command test case
    """

    def __init__(self, testId, cf):
        """ Constructor

        Args:
          testId : test identifier
          cf : dictionary for test specific properties

        """
        self.testId = testId;
        self.cf = cf

    def getPar(self, key):
        """ Getter for test properties

        Args:
          key : key for property

        Returns:
          Value or None  if property not defined

        """
        return _getKey(self.cf, key)

    def getDescr(self):
        """ Getter for description property
        """
        return self.getPar('descr')

    def getTestId(self):
        """ Getter for test id property
        """
        return self.testId

    def isTestCase(self):
        """ Checker if test case is predefined python test case

        Returns:
           True: if predefined python test case
           False: otherwise

        """
        if self.cf.has_key('testcase'): return 1
        return 0

    def getTestCase(self):
        """ Getter for test case property

        Returns:
          Test case name or None if not defined

        """
        return self.getPar('testcase')

    def getCopyTestRes(self):
        """ Getter  for 'copytestres' property
        """

        return self.getPar('copytestres')

    def getCopyCommonRes(self):
        """ Getter for 'copycommonres' property
        """
        return self.getPar('copycommonres')

    def getCommand(self):
        """ Getter for 'command' property
        """
        return self.getPar('command')


class TestParam:

    """ Container for general test suite properties

    Attributes:
      suiteparam : container for test suite run parameters
      cf : dictionary with test suite properties
        can be None if not defined

    """

    def __init__(self, he, suiteparam):
        """ Constructor

        Args:
          he : dictionary with test suite properties (can be None)
          suiteparam : container with test suite run param

        """
        self.cf = he
        self.suiteparam = suiteparam

    def getResDir(self):
        """ Getter for 'resdir' parameter
            (directory where test cases and resources are placed)
        """
        return self.suiteparam.resdir

    def getGlobResDir(self):
        """ Getter for 'globresdir' parameter
            (directory where common resources are located)
        """
        return self.suiteparam.globresdir

    def getTestDir(self, s):
        """ Getter for directory where resource for one test case are located

        Args:
          s : test case identifier

        Returns:
          Path name, directory for test case

        """
        dd = self.suiteparam.resdir
        di = os.path.join(dd, s)
        return di
    
    def getRunDir(self):
        """ Getter for 'run dir' parameter
            (directory where test case is copied and launched)
        """
        return self.suiteparam.rundir

    def getPar(self, key):
        """ Getter for global test suite property

        Args:
          key : parameter key

        Returns:
          value or None if property not defined

        """
        return _getKey(self.cf, key)

    def getCustomC(self):
        """ Getter for 'customC' reference
        """
        return self.suiteparam.customC


def removeDir(te):
    """ Remove directory and all subdirectories.

    Args:
      te : directory name to be removed

    Returns:
      Nothing

    Raise:
      Exception if error

    """
    if not os.path.isdir(te): return
    shutil.rmtree(te)


def copyDir(sou, dest):
    """ Copy directory (with subdirectories)

    Args:
      sou : directory name to be copied from
      dest : directory to be copied to

    Returns:
      Nothing

    Raise:
      Exception if error
    """
    if not os.path.isdir(dest):
#        logging.debug("Copy tree : " + sou + " ==> " + dest)
#        shutil.copytree(sou, dest)
#        return
       logging.debug("Create directory : " + dest)
       os.mkdir(dest)
    li = os.listdir(sou)
    for na in li:
        if na == ".svn" :
          logging.debug(" Ignore " + na)
          continue
        soul = os.path.join(sou, na)
        destl = os.path.join(dest, na)
        if os.path.isfile(soul):
            logging.debug("Copy file : " + soul + " ==> " + destl)
            shutil.copyfile(soul, destl)
        else:
            logging.debug("Copy directory : " + soul + " ==> " + destl)
            copyDir(soul, destl)

def copyFile(param, teparam, file):
    """ Copy  file from test case directory to run directory

    Args:
      param : TestParam container
      teparam: OneTestParam container
      file : file name to be copied

    Returns:
      Nothing

    Raise:
      Exception if error

    """
    assert file != None
    soud = param.getTestDir(teparam.getTestId())
    soufile = os.path.join(soud, file)
    destd = param.getRunDir()
    destfile = os.path.join(destd, file)
    shutil.copy2(soufile, destfile)


def clearRunDir(param):
    """ Clean run directory, removes all files

    Args:
      param : TestParam container

    Returns:
      Nothing

    Raise:
      Exception if error

    """
    tt = param.getRunDir()
    logging.debug("Clear " + tt)
    removeDir(tt)
    if not os.path.isdir(tt):
        os.makedirs(tt)

def __copyRes(test, testId, dest):
    """ Copy resource (command or test case specific) to run directory

    Args:
      test : TestParam container
      testId : if None common resource, test case resource otherwise
      dest : resource description (<name sou> : <name dest>

    Returns:
      Nothing

    Raise:
      Exception if error

    """
    if dest == None: return
    sou = test.getResDir()
    if testId != None:
        sou = test.getResDir()
        sou = test.getTestDir(testId)
    else:
        sou = test.getGlobResDir()
    list = dest.split(":")
    if len(list) == 1:
        soud = list[0]
        destd = soud
    else:
        soud = list[0]
        destd = list[1]
    soudir = os.path.join(sou, soud)
    destdir = os.path.join(test.getRunDir(), destd)
    logging.debug(soudir + " ==> " + destdir)
    copyDir(soudir, destdir)


def prepareRunDir(param, teparam):
    """ Prepare run directory for testcase : cleans and copy resources


    Args:
      param : TestParam container
      teparam : OneTestParam container

    Returns:
      Nothing

    Raise:
      Exception if error

    """
    clearRunDir(param)
    __copyRes(param, None, teparam.getCopyCommonRes())
    __copyRes(param, teparam.getTestId(), teparam.getCopyTestRes())

def compareFile(sou,dest) :
    logging.info("Compare " + sou + " <==> " + dest)
    f1 = open(sou, "r")
    f2 = open(dest, "r")
    li1 = f1.readlines()
    li2 = f2.readlines()
    if len(li1) != len(li2) :
        logging.info(" number of lines is different")
        return False
    for i in range(0, len(li1))  :
        line1 = li1[i].rstrip()
        line2 = li2[i].rstrip()
        if line1 != line2 : 
            logging.info(" line number: " + str(i)  + " different")
            logging.info(line1)
            logging.info(line2)
            return False
	  
# 2011/08/30 - filecmp.cmp replace by manual comparing to avoid trailing whitespaces
#        eq = filecmp.cmp(sou, dest)
#        if not eq:
 #           logging.info("  different")
 #           res = 0
    return True

def compareFiles(param, teparam, testdir, patt, destdir):
    """ Compare files in test case resource directory and test dir

    Args:
      param : TestParam container
      teparam: OneTestParam container
      testdir : subdirectory in test case resource with files to compare
      patt : file pattern for file to be compared
      destdir : subdirectory in run dir containing files to be compares

    Returns:
      True: all files are the same
      False: at least one file is different

    Raise:
      Exception if any error

    """    
    t = param.getTestDir(teparam.getTestId())
    xdir = os.path.join(t, testdir)
    logging.debug("Comparing file, open directory " + xdir)
    if not os.path.isdir(xdir): 
      logging.debug("Empty directory, exiting")
      return True
    li = os.listdir(xdir)
    tdir = param.getRunDir()
    res = True
    for l in li:
        logging.debug(l + " found")
        if l.find(patt) == -1: 
	   logging.debug("Not conform to pattter " + patt + ", ignored")
	   continue
        sou = os.path.join(xdir, l)
        dest = os.path.join(tdir, destdir)
        dest = os.path.join(dest, l)
        logging.info(sou + " <=> " + dest)
        if not os.path.isfile(dest):
            logging.info ("  " + dest + " - does not exist")
            res = False
            continue
	if not compareFile(sou,dest) : res = False
	
    return res

class SampleTestCase(unittest.TestCase):
    """ Sample test case, do nothing

    Attributes:
      param : TestParam container
      teparam : OneTestParam container

    """

    def __init__(self, param, teparam):
        unittest.TestCase.__init__(self, 'runTest')
        self.param = param
        self.teparam = teparam

    def setUp(self):
        prepareRunDir(self.param, self.teparam)

    def runTest(self):
        print self.teparam.getDescr()
