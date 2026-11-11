import os 
import sys 
import json
import hashlib #it coverts into hexadecima


def add(file_path):
    repo_path=".minigit"
    if not os.path.isdir(repo_path): #it will check weather the hidden directory exists
        print("MiniGit repository not found.")
        return

    if not os.path.isfile(file_path): #check weather the file you eant to add is exiat or not
       print("File does not exist.")
       return
    file_path=os.path.normpath(file_path) #directly connects to folder
    if file_path==".minigit" or file_path.startswith(".minigit"+os.sep):
       print("Cannot stage MiniGit metadata.")
       return 
    
    with open(file_path, "rb")as file: #reads the adding file data
         file_data=file.read()
    file_hash =hashlib.sha1(file_data).hexdigest()
    object_path = os.path.join(repo_path, "objects", file_hash)
   #we are converinting and saving into file_hash  and that converted data in objects
    
    if not os.path.exists(object_path):
       with open(object_path, "wb")as objects_file:
          objects_file.write(file_data) 
    index_path = os.path.join(repo_path, "index")
    with open(index_path, "r") as index_file:
        index = json.load(index_file) #convert formated data into json data
    index[file_path]=file_hash
    with open(index_path, "w")as index_file: #saving the updated data
        json.dump(index, index_file, indent=4) #tihs line will arrange index data properly
    print("staged:", file_path)#displayes a succcess message

if __name__ == "__main__":
   if len(sys.argv) != 2: #if we dont write command properly this will tell us
      print("Usage: python3 add.py <filename>")
   else:
       add(sys.argv[1])
