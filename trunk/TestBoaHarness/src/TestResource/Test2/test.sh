#!/bin/sh
if ! test -d out;  then exit 1; fi
if test -f out/file1.txt; then exit 0; fi
if test -f out/file2.txt; then exit 0; fi
exit 1
