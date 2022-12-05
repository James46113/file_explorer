import os, shutil
import tkinter as tk
from os.path import isfile, join
from colorama import Fore, Style

currentDir = "/"
showHidden = False

def printBold(string: str, end="\n") -> None:
    print(Style.BRIGHT + string + Style.RESET_ALL, end=end)

def printError(string: str, end="\n") -> None:
    print(Style.BRIGHT + Fore.RED + string + Fore.RESET + Style.RESET_ALL, end=end)

while True:
    contents = os.listdir(currentDir)
    files = [file for file in contents if isfile(join(currentDir, file))]
    dirs = [directory for directory in contents if not isfile(join(currentDir, directory))]
    cmd = input(currentDir + ">> ").strip()

    try:
        if cmd == "exit":
            break

        elif cmd.startswith("ls"):
            try:
                if cmd.split(" ")[1] == "-f":
                    showHidden = True
            except IndexError:
                pass
            if cmd == "ls" or showHidden:
                if len(dirs) > 0:
                    printBold(Fore.LIGHTGREEN_EX + "Directories: ")
                    for directory in dirs:
                        if directory[0] != "." or showHidden:
                            print(Fore.LIGHTBLUE_EX + directory)

                if len(files) > 0:
                    printBold(Fore.LIGHTGREEN_EX + "Files: ")
                    for file in files:
                        if file[0] != "." or showHidden:
                            print(Style.RESET_ALL + file)
            showHidden = False

        elif cmd.split(" ")[0] == ("cd"):
            try:
                if cmd[3:] not in dirs:
                    os.listdir(cmd[3:])
                    currentDir = cmd[3:]
                else:
                    raise Exception
            except:
                if cmd[3:] == "~":
                    currentDir = "/home/james"
                elif cmd[3:] in dirs:
                    if currentDir == "/":
                        currentDir = ""
                    currentDir += "/" + cmd[3:]
                elif cmd[3:] == "..":
                    currentDir = "/".join(currentDir.split("/")[:-1])
                    if currentDir == "":
                        currentDir = "/"
                else:
                    printError("No such directory")            

        elif cmd.split(" ")[0] == ("rm"):
            if cmd.split(" ")[1] == "-r":
                if cmd[6:] in dirs:
                    shutil.rmtree(join(currentDir, cmd[6:]))
                else:
                    printError("No such directory")
            else:
                if cmd[3:] in files:
                    os.remove(join(currentDir, cmd[3:]))
                else:
                    printError("No such file")
        
        elif cmd.split(" ")[0] == "touch":
            with open(cmd[6:], "w") as f:
                pass

        elif cmd.split(" ")[0] == "mkdir":
            os.mkdir(join(currentDir, cmd.split(" ")[1]))

        else:
            printError("Invalid Command")
    except IndexError as e:
        printError(f"Invalid Command: {e}")