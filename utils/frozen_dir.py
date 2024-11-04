# -*- coding: utf-8 -*-
import sys
import os


def app_path():
    """Returns the base application path."""
    if hasattr(sys, 'frozen'):
        # Handles PyInstaller
        return os.path.dirname(sys.executable)
    return os.path.dirname(__file__)

def savelog(file,log):
    dirname = os.path.dirname(file)
    if not os.path.exists(dirname):
        os.mkdir(dirname)
    with open(file,'a',encoding='utf-8') as f:
        f.write(log+'\n')