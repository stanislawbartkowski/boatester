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

"""NZ PDA test case helper
"""

__authors__ = [
    '"Stanislaw Bartkowski" <stanislawbartkowski@gmail.com>',
]

import sys

from TestCaseHelper import *

NZTEST="nztest.scen"

NZSCRIPT="nzscript:"
NZPATHSCRIPT="nzpathscript:"
COMMENT="#"
NZSQL='nzsql'
OUT='out'
VERIFY='verify'
EXT=".txt"
PATHSH="runpathsh:"
SQL="sql:"
VERIFYCOM="verify:"
OUTTEMP="temp"
RUNSH="runsh:"

def _getParam(commandparam) :
    """ Untangle the command param 
    Params: 
        commandparam : string where elements are delimited by |
    Returns:
        (script,out,verirfy,addparam)    
    """
    t = commandparam.split('|')
    out = None
    verify=False
    script = t[0].strip()
    addparam = None
    if len(t) >= 2 and t[1].strip() != "" : out = t[1].strip() + EXT;
    if len(t) >= 3 and t[2].strip() != "" :
        if t[2].strip() != VERIFY : raise TestCaseHelper.TestException(commandparam + " - third element (" + t[2].strip() + ") should be " + VERIFY + " or empty")
        verify = True
    if len(t) == 4 : addparam = t[3]
    return (script,out,verify,addparam)

class NZSQLScriptHelper :
    
    def __init__(self,testcase,param, teparam) :
        self.testcase = testcase
        self.param = param
        self.teparam = teparam
        self.sqlparam = None
      
    def _getFileName(self,filename) :
        testfile = getResourceDirPath(self.teparam,self.param,filename)
        exist(testfile)
        return testfile
    
    def _getTextOutDir(self) :
        return getResourceDirPath(self.teparam,self.param,OUT)
    
    def _sqlStarted(self) :
        return self.sqlparam != None

    def _runcommand(self,command,commandparam) :
        (scriptname,outfile,verify,addparam) = _getParam(commandparam)
        outputdir = os.path.join(self.param.getRunDir(),OUT)
        if not os.path.exists(outputdir) : os.mkdir(outputdir)
        if addparam != None : commands = command + " " + addparam
        else : commands = command
        if outfile != None :
            if outfile == OUTTEMP : output = getTmpName(outputdir)
            else : output = os.path.join(outputdir,outfile)
            res = runBin(self.param, commands + " >" + output, None)
            os.system("cat " + output)
        else : res = runBin(self.param, commands, None)
        if verify :
            # verify the return code
            self.testcase.assertTrue(res == 0,commands + " returned " + str(res))
            if outfile != None :
                # compare the actual result agains the current result
                destfile = self._getFileName(os.path.join(OUT,outfile))
                self.testcase.assertTrue(compareFile(output,destfile))      
                                  
    def _getnzsqlpath(self) :                                  
        nzsql = self._getP(NZSQL)
        resDir = self.param.getGlobResDir()
        return os.path.join(resDir,nzsql)
                                  
    def _executepathnzsql(self,commandparam) :
        (scriptname,outfile,verify,addparam) = _getParam(commandparam)
        exist(scriptname)
        nzsqlpath = self._getnzsqlpath()
        self._runcommand(nzsqlpath + " -f " + scriptname,commandparam)

    def _executenzsql(self,commandparam) :
        (scriptname,outfile,verify,addparam) = _getParam(commandparam)
        scriptpath=self._getFileName(scriptname)
        nzsqlpath = self._getnzsqlpath()
        self._runcommand(nzsqlpath + " -f " + scriptpath,commandparam)

    def _executebash(self,commandparam) :        
        (scriptname,outfile,verify,addparam) = _getParam(commandparam)
#      exist(scriptname)
        self._runcommand(scriptname,commandparam)
      
    def _executesh(self,commandparam) :
        (scriptname,outfile,verify,addparam) = _getParam(commandparam)
        scriptlocal = self._getFileName(scriptname)
        self._runcommand(scriptlocal,commandparam)
      
    def _executesql(self,commandparam) :
        if not self._sqlStarted() :
            self.sqlparam = commandparam
            self.sqlcommand = "";
            return
        (startsql,outfile,verify,addparam) = _getParam(self.sqlparam)
        nzsqlpath = self._getnzsqlpath()
        self._runcommand(nzsqlpath + " -c \"" + startsql + " " + self.sqlcommand + "\"",self.sqlparam)	
        self.sqlparam = None
      
    def _verify(self, param) :
        outresdir = self._getFileName(OUT)	  
        outputdir = os.path.join(self.param.getRunDir(),OUT)
        compareFiles(self.param, self.teparam, outresdir, EXT, outputdir)      
      
    def _getP(self,key) :
        return getParam(self.teparam,self.param,key)
      
    def _parseLine(self,line,listofc) :
        if line.strip() == "" : return (None,None)
        if line.startswith(COMMENT) : return (None,None) 
        for co in listofc :
            if line.startswith(co) : 
                return (co,line[len(co):].strip())
        if self._sqlStarted() :
            self.sqlcommand = self.sqlcommand + " " + line.strip()
            return (None,None)       
        TestException(line + " unrecognized command, should start with "+str(listofc))
                   
    def run(self) :
        testfile = self._getFileName(NZTEST)
        p = lambda key : self._getP(key)
        logging.debug("Reading test scenario from %s",testfile)
        lines = readListOfLinesWithReplace(testfile, p)
        listofc = [ NZSCRIPT,PATHSH,SQL,VERIFYCOM, RUNSH, NZPATHSCRIPT ]
        for l in lines :
            (comm,param) = self._parseLine(l,listofc)
            if comm == None : continue;
            logging.debug("Command: %s Param : %s",comm,param)
            if comm == NZSCRIPT : self._executenzsql(param)
            if comm == PATHSH : self._executebash(param)
            if comm == SQL : self._executesql(param)
            if comm == VERIFYCOM : self._verify(param)
            if comm == RUNSH : self._executesh(param)
            if comm == NZPATHSCRIPT : self._executepathnzsql(param)

class NZPDATestCase(unittest.TestCase):

    def __init__(self, param, teparam):
        unittest.TestCase.__init__(self, 'runTest')
        self.param = param
        self.teparam = teparam

    def setUp(self):
        prepareRunDir(self.param, self.teparam)
        
    def runTest(self):
        NZSQLScriptHelper(self,self.param,self.teparam).run()

class NZPDAFactory:

    def constructTestCase(self, param, tepar):
        nztest = tepar.getPar('nztest')
        if nztest == None : return None
        nzsql = getParam(param,tepar,NZSQL)
        teca = NZPDATestCase(param, tepar)
        return [teca]
