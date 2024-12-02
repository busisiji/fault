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


def validate_directory(directory):
    if not os.path.isdir(directory):
        raise ValueError("无效的目录路径")
    if any(char in directory for char in ['..',  '\\']):
        raise ValueError("非法路径字符")

def exists_path(directory):
    """检查目录是否存在，如果不存在则创建"""
    if not os.path.exists(directory):
        os.makedirs(directory)