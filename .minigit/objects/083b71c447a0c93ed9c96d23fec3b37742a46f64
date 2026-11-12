import os #create and check directories
def init():
    repo_path = ".minigit"
    if os.path.exists(repo_path): #checks eather directory exists or not
        print("MiniGit repository already exists.")
        return
    os.makedirs(os.path.join(repo_path, "objects")) #creates objects inside .minigit 
    os.makedirs(os.path.join(repo_path, "refs", "heads"))
    head_path=os.path.join(repo_path, "HEAD")
    with open(head_path, "w") as head_file:
         head_file.write("ref: refs/heads/main\n")
    index_path = os.path.join(repo_path,"index")
    with open(index_path, "w") as index_file:
         index_file.write("{}") #gives a empty string area in the file JSON object
    print("Initilized empty MiniGit repository.")

if __name__ == "__main__":
    init()
