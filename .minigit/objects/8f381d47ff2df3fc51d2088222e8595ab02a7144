
#!/bin/bash

# Initialize MiniGit
python3 init.py

# Create some files
nano file1.txt
nano file2.txt
nano file3.txt
nano file4.txt

# Check repository status
python3 status.py

# Add files one by one
python3 add.py file1.txt
python3 status.py

python3 add.py file2.txt file3.txt
python3 status.py

# Add all remaining files
python3 add.py .
python3 status.py

# Commit the changes
python3 commit.py -m "Initial commit"
python3 status.py

# Delete a file and check the difference
rm file4.txt
python3 diff.py

# Restore the deleted file
python3 restore.py file4.txt

# Create a new branch
python3 branch.py
python3 branch.py newbranch

# Switch to the new branch
python3 switch.py newbranch

# Create a file on the new branch
nano newfile.txt

# Add and commit the new file
python3 add.py newfile.txt
python3 commit.py -m "Add newfile on newbranch"

# Switch back to main
python3 switch.py main

# Merge the new branch into main
python3 merge.py newbranch

# Check the merged file
cat newfile.txt

# Check repository status
python3 status.py

# View commit history
python3 log.py

# List project files
ls
