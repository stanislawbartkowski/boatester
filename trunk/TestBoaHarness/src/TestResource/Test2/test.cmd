echo "Check out1\file1.txt"
if not exist "out\file1.txt" exit 1
echo "Check out1\file2.txt"
if not exist "out\file2.txt" exit 1
echo "OK. exists"