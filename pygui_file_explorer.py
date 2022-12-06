import dearpygui.dearpygui as dpg
import os, time, subprocess, platform, shutil, threading
from datetime import datetime
from os.path import join, isfile, getsize, getmtime

def update_files():
    global currentPath, showHidden, temp_files, temp_dirs, temp_dirs_display, temp_files_display
    temp_files_display = [found_file for found_file in [format_file(file) for file in os.listdir(currentPath) if isfile(join(currentPath, file)) and (file[0] != "." or showHidden)] if found_file != "--FILE-ERROR--"]
    temp_dirs_display  = [found_dir for found_dir in [format_file(directory) for directory in os.listdir(currentPath) if not isfile(join(currentPath, directory)) and (directory[0] != "." or showHidden)] if found_dir != "--FILE-ERROR--"]
    temp_files = [(file) for file in os.listdir(currentPath) if isfile(join(currentPath, file)) and (file[0] != "." or showHidden)]
    temp_dirs  = [(directory) for directory in os.listdir(currentPath) if not isfile(join(currentPath, directory)) and (directory[0] != "." or showHidden)]

    temp_dirs.insert(0, "..")
    temp_dirs_display.insert(0, "..")
    temp_files.sort()
    temp_dirs.sort()
    temp_files_display.sort()
    temp_dirs_display.sort()
    temp_path_contents = temp_dirs_display + temp_files_display
    dpg.configure_item(item="currentPath", default_value=currentPath)
    dpg.configure_item(item="filesBox", items=temp_path_contents)

def format_file(filename: str):
    global currentPath, temp_dirs
    try:
        temp_filename = filename
        if len(filename) > 25:
            temp_filename = filename[:22] + "..."
        temp = temp_filename + " "*(30-len(temp_filename))

        size = getsize(join(currentPath, filename))

        if size < 1000: size = str(round(size, 1)) + "B"
        elif size < 100000: size = str(round(size/1000, 1)) + "KB"
        elif size < 10000000: size = str(round(size/1000000, 1)) + "MB"
        else: size = str(round(size/1000000000, 1)) + "GB"

        temp += size + " "*(30-len(size))
        
        if not isfile(join(currentPath, filename)):
            temp += "directory" + " "*18
        else:
            temp_type = filename.split(".")[-1]
            if "." not in filename:
                temp_type = "file"
            elif len(temp_type) > 25:
                temp_type = filename.split(".")[-1][:22] + "..."
            temp += temp_type + " "*(27-len(temp_type))
        
        temp += str(datetime.fromtimestamp(getmtime(join(currentPath, filename)))).split(".")[0]
        return temp
    except Exception as e:
        return "--FILE-ERROR--"
    

def change_dir(sender, app_data, user_data):
    global currentPath, last_click, last_clicked, temp_dirs, operatingSystem, temp_dirs_display
    current_click = int(time.time())*1000
    if current_click - last_click < 5 and last_clicked == app_data:
        if app_data in temp_dirs_display:
            ind = temp_dirs_display.index(app_data)
            try:
                if temp_dirs[ind] == "..":
                    currentPath = "/".join(currentPath.split("/")[:-2]) + "/"
                else:
                    currentPath += temp_dirs[ind] + "/"
                update_files()
            except PermissionError:
                currentPath = "/".join(currentPath.split("/")[:-2]) + "/"
                update_files()
                show_error("Permission Denied")
        else:
            ind = temp_files_display.index(app_data)
            if operatingSystem == "Windows":
                print("opening file")
                os.startfile(join(currentPath, temp_files[ind]))
            else:
                print("opening file")
                subprocess.call(("xdg-open", join(currentPath, temp_files[ind])))
    last_click = current_click
    last_clicked = app_data

def toggle_hidden(sender, app_data, user_data):
    global showHidden
    if showHidden:
        showHidden = False
        dpg.configure_item(item="hideFilesButton", label="Show hidden\n   files")
    else:
        showHidden = True
        dpg.configure_item(item="hideFilesButton", label="Hide hidden\n   files")
    update_files()

def nav_home():
    global currentPath
    currentPath = os.path.expanduser('~').replace("\\", "/") + "/"
    update_files()

def nav_root():
    global currentPath
    currentPath = "/"
    update_files()

def pathChanged(sender, app_data, user_data):
    global currentPath
    try:
        tempPath = dpg.get_value("currentPath")
        if tempPath[-1] != "/":
            tempPath += "/"
        os.listdir(tempPath)
        currentPath = tempPath
        update_files()
    except FileNotFoundError as e:
        dpg.set_value("currentPath", currentPath)
    except PermissionError:
        show_error("Permission Denied")
        dpg.set_value("currentPath", currentPath)


def mkdir(sender, app_data, user_data):
    def set_dir_to_make(sender, app_data, user_data):
        global dir_to_make, currentPath
        dir_to_make = dpg.get_value("dirName")
        try:
            os.mkdir(join(currentPath, dir_to_make))
        except FileExistsError as e:
            show_error("Directory already exists")
        except Exception:
            show_error("Bad directory name")
        update_files()
        dpg.delete_item("dialogueWindow")

    with dpg.window(tag="dialogueWindow", pos=(400, 250), width=200, height=100, label="Enter Directory Name", no_collapse=True, no_move=True):
        dpg.add_input_text(tag="dirName", hint="Directory Name", width=180, pos=(10, 50))
    with dpg.item_handler_registry(tag="dialogue handler"):
        dpg.add_item_deactivated_after_edit_handler(callback=set_dir_to_make)        
    dpg.bind_item_handler_registry("dirName", "dialogue handler")

def mkfile(sender, app_data, user_data):
    def set_file_to_make(sender, app_data, user_data):
        global currentPath
        file_to_make = dpg.get_value("fileName")
        try:
            with open(file_to_make, "w") as f:
                pass
        except FileExistsError as e:
            show_error("File already exists")
        except Exception:
            show_error("Bad file name")
        update_files()
        dpg.delete_item("dialogueWindow")

    with dpg.window(tag="dialogueWindow", pos=(400, 250), width=200, height=100, label="Enter File Name", no_collapse=True, no_move=True):
        dpg.add_input_text(tag="fileName", hint="File Name", width=180, pos=(10, 50))
    with dpg.item_handler_registry(tag="dialogue handler2"):
        dpg.add_item_deactivated_after_edit_handler(callback=set_file_to_make)        
    dpg.bind_item_handler_registry("fileName", "dialogue handler2")


def show_error(msg: str):
    with dpg.window(tag="errorWindow", pos=(400, 250), width=200, height=100, label="Error", no_collapse=True, no_move=True):
        dpg.add_text(tag="msg")
    dpg.set_value("msg", msg)

def delfile():
    global last_clicked, currentPath, temp_files, temp_files_display, temp_dirs_display, temp_dirs
    try:
        if last_clicked in temp_files_display:
            ind = temp_files_display.index(last_clicked)
            os.remove(join(currentPath, temp_files[ind]))
        elif last_clicked in temp_dirs_display:
            ind = temp_dirs_display.index(last_clicked)
            shutil.rmtree(join(currentPath, temp_dirs[ind]))
        else:
            show_error("No such file or directory")

    except PermissionError:
        show_error("Permission Denied")
    update_files()

def rename():
    def set_new_name(sender, app_data, user_data):
        global currentPath, last_clicked
        new_name = dpg.get_value("fileName")
        try:
            if last_clicked in temp_files_display:
                ind = temp_files_display.index(last_clicked)
                os.replace(join(currentPath, temp_files[ind]), join(currentPath, new_name))
            elif last_clicked in temp_dirs_display:
                ind = temp_dirs_display.index(last_clicked)
                os.replace(join(currentPath, temp_dirs[ind]), join(currentPath, new_name))
        except PermissionError:
            show_error("Permission Denied")
        except Exception:
            show_error("Bad file name")
        update_files()
        dpg.delete_item("dialogueWindow")

    with dpg.window(tag="dialogueWindow", pos=(400, 250), width=200, height=100, label="Enter New Name", no_collapse=True, no_move=True):
        dpg.add_input_text(tag="fileName", hint="New Name", width=180, pos=(10, 50))
    with dpg.item_handler_registry(tag="dialogue handler2"):
        dpg.add_item_deactivated_after_edit_handler(callback=set_new_name)        
    dpg.bind_item_handler_registry("fileName", "dialogue handler2")

def update_files_bg():
    while True:
        update_files()
        time.sleep(1)
    
def keyhandler(sender, app_data, user_data):
    if dpg.is_key_pressed(dpg.mvKey_Delete):
        delfile()

last_click = 0
last_clicked = 0
currentPath = "/"
showHidden = False
temp_files = []
temp_dirs = []
temp_files_display = []
temp_dirs_display = []
operatingSystem = platform.system()

dpg.create_context()
dpg.create_viewport(title='File Explorer', width=1000, height=600)

with dpg.window(tag="filesWindow", pos=(200, 100), width=800, height=500, label=(currentPath), no_title_bar=True, no_collapse=True, no_close=True, no_move=True):
    dpg.add_input_text(default_value="/", tag="currentPath", callback=None, width=780)
    dpg.add_text("Name" + " "*26 + "Size" + " "*26 + "Type" + " "*23 + "Last Modified")
    dpg.add_listbox(tag="filesBox", width=780, num_items=24, callback=change_dir)

with dpg.window(tag="Settings Window", pos=(0, 0), width=1000, height=100, no_collapse=True, no_move=True, no_close=True, no_title_bar=True):
    dpg.add_button(tag="hideFilesButton", label="Show hidden\n   files", callback=toggle_hidden, width=100, height=50, pos=(10, 25))
    dpg.add_button(tag="mkdir", label="  Create\nDirectory", width=100, height=50, pos=(120, 25), callback=mkdir)
    dpg.add_button(tag="mkfile", label="Create\n File", width=100, height=50, pos=(230, 25), callback=mkfile)
    dpg.add_button(tag="delfile", label=" Delete\nSelected", width=100, height=50, pos=(340, 25), callback=delfile)
    dpg.add_button(tag="rename", label=" Rename\nSelected", width=100, height=50, pos=(450, 25), callback=rename)

with dpg.window(tag="sideFrame", width=200, height=500, pos=(0, 100), no_collapse=True, no_move=True, no_close=True, no_title_bar=True):
    dpg.add_text("Quick Navigation")
    dpg.add_button(label="Root", callback=nav_root, width=180, height=20, pos=(10, 40))
    dpg.add_button(label="Home", callback=nav_home, width=180, height=20, pos=(10, 80))

with dpg.item_handler_registry(tag="widget handler"):
    dpg.add_item_deactivated_after_edit_handler(callback=pathChanged)
    dpg.add_key_release_handler(key=dpg.mvKey_Delete)

t = threading.Thread(target=update_files_bg)
t.daemon = True
t.start()
dpg.bind_item_handler_registry("currentPath", "widget handler")
update_files()
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()