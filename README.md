Boa is very simple test framework written in Python. It is an extension of Python's unit test package. It is platform independent, the only prerequisite is Python itself.

More information : [Wiki](https://github.com/stanislawbartkowski/boatester/wiki)

Also can be run on Jython - Python implementation running on JVM platform. In that case the prerequisite is JRE and Jython package.

It consists only of two Python's modules and a few classes and methods. The purpose was to create framework as simple as possible. Developer/tester should focus on writing and running test cases, not to struggle with the test tool.

## Some features of Boa test framework ##

  * Automatic discovery of test cases. Every test case has its own directory (with subdirectories). So to add new test case to the test suite just create next subdirectory in the test suite directory. Test case directory should contain all resources needed to run this test. It is possible to have a common resources shared by more than one test case.

  * Possibility to extend test case types (in Python). If you have more than one test case using the same pattern (for instance: take some data, run a program or do something, evaluate the result) one can define reusable custom test case handler (type)

  * Two test case types are predefined:
    * Run a program (binary, shell script, bat script) and propagate test result (passed / failed) by exit code
    * Run a python unittest TestSuite object. http://docs.python.org/library/unittest.html#testsuite-objects. Test result is propagated by unittest assertion methods.

Start now: [GettingStarted.md]

Advanced: http://code.google.com/p/boatester/wiki/AdvancedBoaTester

## Future extension ##

Remote deploying and remote testing.

## New version ##
2013/03/17

Tested with Selenium 2.
New features related to selenium based test cases.
* Automatic starter for 'selenium' based test cases. It is possible to run tests without Python test case started. Using Python started (more flexible) is still possible and can be mingled with test cases started automatically
* 'call' command. Allows reusing pieces of coded between different test case or inside one test case.
* New 'select' and 'waitForNot' command.

## New version ##
2012/12/26

SQL/ODBC testing is possible now. It is possible the unit testing of SP (stored procedure) and UDF (user defined functions).
[Description](http://code.google.com/p/boatester/wiki/SqlUnitTesting?ts=1356557332&updated=SqlUnitTesting)

## New feature added ##

Helper for selenium based test written in Python.

http://code.google.com/p/boatester/wiki/SeleniumHelper

## New version ##
2011/09/11

I changed a method for file comparing. Instead of standard 'comp' function I'm using manual line by line comparing to avoid LF/CR hell.

## New version ##
2011/07/04

Interpolation in selenium.file ("macro" substitution).

http://hoteljavaopensource.blogspot.com/2011/07/boatester-new-version.html

## New version ##
2011/06/02

Two new features:

  1. Three environment variable are define and can be referenced in test.properties configuration file by : %(variable name)s
  1. Selenium extension: parameter 'dirtestcase' has been added. Python test case can be read from another directory - although selenium test is read from test case resource directory. This was several test cases can use the same python test case and run different selenium.file scenario, just avoiding code duplication.

## 2011/01/01 ##

'selectCombo' added to SeleniumHelper.


## New feature added ##
2010/12/19

'Disabled' file in test case directory to ignore test case.
