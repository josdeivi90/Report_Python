import os

def list_files_in_folder(dir):
    return os.listdir(dir)

def clean_folder(dir):
    list_files = list_files_in_folder(dir)
    for f in list_files:
        os.remove(os.path.join(dir, f))
