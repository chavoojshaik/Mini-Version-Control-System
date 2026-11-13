python3 init.py

nano file1.txt
nano file2.txt
nano file3.txt
nano file4.txt

python3 status.py

python3 add.py file1.txt
python3 status.py
python3 add.py file2.txt file3.txt
python3 status.py
python3 add.py .
python3 status.py

python3 commit.py -m "our first commit"

python3 status.py

rm file4.txt

python3 diff.py

python3 branch.py

python3 branch.py newbranch

python3 switch.py newbranch

nano newfile.txt

python3 switch.py main

python3 merge.py newbranch

python3 status.py

rm newfile.txt

python3 restore.py 

ls

python3 status.py

