from os import mkdir
from os.path import isdir

if not isdir('upload_file'):
    mkdir('upload_file')
