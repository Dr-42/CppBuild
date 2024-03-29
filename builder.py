import hashlib
import subprocess
import platform
import os
from termcolor import colored

# Output details

out_file = 'main'
out_type = 'exe'
# Directories
out_dir = 'bin'
obj_dir = 'obj'
src_dir = 'src'

#Compiler options
compiler = 'g++'
libs    = '-lm'
cflags  = '-g -std=c++17'

##########################################
##### DO NOT EDIT BELOW THIS LINE ########
##########################################

# Global variables
srcs = {}
objs = {}
src_incs = {}
md5s = {}
incs = {}
bins = {}
md5s_to_update = {}

out_ext = ''

if out_type == 'dll':
    if platform.system() == 'Windows':
        cflags += ' -shared'
        out_ext = '.dll'
    elif platform.system() == 'Linux':
        cflags += ' -fPIC -shared'
        out_ext = '.so'
elif out_type == 'exe':
    if platform.system() == 'Windows':
        out_ext = '.exe'
    elif platform.system() == 'Linux':
        out_ext = ''

def run_ps(cmd, print_output=True):
    completed = subprocess.run(["powershell", "-Command", cmd], capture_output=True)
    if print_output:
        if(completed.stderr.decode('utf-8') != ''):
            print(colored('[ERROR] ', 'red'), completed.stderr.decode('utf-8'))
        if(completed.stdout.decode('utf-8') != ''):
            print(colored('[INFO] \n', 'green'), completed.stdout.decode('utf-8'))
    return completed
     
# Saves md5s to file
def save_md5():
    if platform.system() == 'Windows': 
        run_ps('Remove-Item md5.txt; New-Item md5.txt', False)
    elif platform.system() == 'Linux':
        os.system('rm md5.txt && touch md5.txt')
    else:
        print(colored('[ERROR] ', 'red'), 'Unsupported platform')

    for file in md5s.keys():
        if file in md5s_to_update.keys():
            md5s[file] = md5s_to_update[file]
    with open('md5n.txt', 'w') as f:
        for key in md5s:
            f.write(key + ' ' + md5s[key] + '\n')
    if platform.system() == 'Windows': 
        run_ps('Remove-Item md5.txt; Rename-Item -Path md5n.txt -NewName md5.txt', False)
    elif platform.system() == 'Linux':
        os.system('rm md5.txt && mv md5n.txt md5.txt')
    else:
        print(colored('[ERROR] ', 'red'), 'Unsupported platform')


# Loads md5s from file
def load_md5():
    if not os.path.exists('md5.txt'):
        print(colored('[INFO] ', 'green'), 'Creating md5.txt')
        if platform.system() == 'Windows': 
            run_ps('New-Item md5.txt', False)
        elif platform.system() == 'Linux':
            os.system('touch md5.txt')
        else:
            print(colored('[ERROR] ', 'red'), 'Unsupported platform')
        save_md5()

    with open('md5.txt', 'r') as f:
        for line in f:
            line = line.strip()
            if line == '':
                continue
            key, value = line.split(' ')
            md5s[key] = value
    
#Checks if file has been updated
def check_file_updated(long_filename):
    with open(long_filename, 'rb') as f:
        contents = f.read()
    md5 = hashlib.md5(contents).hexdigest()
    if long_filename in md5s.keys():
        if md5s[long_filename] == md5:
            print(colored('[LOG] ', 'blue') ,'File not updated: ' + long_filename)
            return False
        else:
            print(colored('[INFO] ', 'yellow'), 'File updated: ' + long_filename)
            if (not long_filename in md5s_to_update.keys()) and (long_filename in md5s.keys()):
                md5s_to_update[long_filename] = md5
            return True
    else:
        md5s[long_filename] = md5
        print(colored('[LOG] ', 'green') ,'File added: ' + long_filename)
        return True

#parses file for includes
#outputs dictionary
#src_incs = {'long_filename.cpp': ['include1', 'include2']}
def parse_for_includes(long_filename):
    with open(long_filename, 'r') as f:
        for line in f:
            if line.startswith('#include "'):
                line = line.strip()
                line = line.replace('#include', '')
                line = line.replace('"', '')
                line = line.replace('\n', '')
                line = line.strip()
                if long_filename not in src_incs.keys():
                    src_incs[long_filename] = []
                if line not in src_incs[long_filename]:
                    src_incs[long_filename].append(line)

#generates the include command for filepath
def get_inc_cmd(long_filename):
    cmd = ''
    cmds = []
    if long_filename in src_incs.keys():
        for inc in src_incs[long_filename]:
            incfile = inc.split('/')[-1]
            incdir = incs[incfile].removesuffix(inc)
            c = ' -I' + incdir
            if c not in cmds:
                cmds.append(c)
                cmd += c
    return cmd

#gets the sources
#output global
#srcs = {'filename.cpp': 'filepath'}
#incs = {'filename.h': 'filedir'}
def get_srcs(source_dir):
    for root, _, files in os.walk(source_dir):
        for file in files:
            if file.endswith('.cpp') or file.endswith('.c'):
                if platform.system() == 'Windows':
                    srcs[file] = os.path.join(root, file).replace('\\', '/')
                elif platform.system() == 'Linux':
                    srcs[file] = os.path.join(root, file)
            if file.endswith('.h'):
                if platform.system() == 'Windows':
                    incs[file] = os.path.join(root, file).replace('\\', '/')
                elif platform.system() == 'Linux':
                    incs[file] = os.path.join(root, file)

#builds obj files for source_dir into obj_dir
def build_objects(source_dir, obj_dir):
    get_srcs(source_dir)
    if not os.path.exists(obj_dir):
        os.system('mkdir ' + obj_dir)
    for src in srcs:
        compile = False
        if srcs[src].endswith('.cpp'):
            obj = srcs[src].split('/')[-1].replace('.cpp', '.o')
        elif srcs[src].endswith('.c'):
            obj = srcs[src].split('/')[-1].replace('.c', '.o')
        obj = obj_dir + '/' + obj
        objs[src] = obj
        parse_for_includes(srcs[src])
        if check_file_updated(srcs[src]):
            print(colored('[INFO] ', 'green'), 'Compiling ' + srcs[src])
            compile = True
        if srcs[src] in src_incs.keys():
            for inc in src_incs[srcs[src]]:
                incfile = inc.split('/')[-1]
                if check_file_updated(incs[incfile]):
                    print(colored('[INFO] ', 'green'), 'Compiling ' + srcs[src] + ' due to update to ' + incs[incfile])
                    compile = True
        if compile:
            compile_obj(srcs[src], obj)

compiled_obj = False
#compiles filepath.cpp to obj
def compile_obj(filepath, obj):
    cmd = compiler + ' ' + cflags + ' -c -o ' + obj + ' ' + filepath + get_inc_cmd(filepath)
    print(colored('[LOG] ', 'blue') ,cmd)
    error_code = os.system(cmd)
    if error_code != 0:
        print(colored('[ERROR] ', 'red'), 'Error compiling ' + filepath)
        exit(error_code)
    else:
        print(colored('[LOG] ', 'green') ,'Compiled ' + filepath)
        global compiled_obj
        compiled_obj = True
        save_md5()

#links obj files into bin
def link():
    if not os.path.exists(out_dir):
        if platform.system() == 'Windows':
            run_ps('New-Item ' + out_dir + ' -ItemType Directory')
        elif platform.system() == 'Linux':
            os.system('mkdir ' + out_dir)
    if not os.path.exists(out_dir + '/' + out_file + out_ext):
        up_exec = True
    else:
        up_exec = check_file_updated(out_dir + '/' + out_file + out_ext)

    if not compiled_obj and not up_exec:
        print(colored('[LOG] ', 'blue') ,'Nothing to be compiled')
        return
    objtot = ''
    i = 0
    for obj in objs:
        objtot += ' ' + objs[obj]
        i += 1
    cmd = compiler + ' ' + cflags + ' -o ' + out_dir + '/' + out_file + out_ext + objtot + ' ' + libs
    print(colored('[LOG] ', 'blue') ,cmd)
    error = os.system(cmd)
    if error != 0:
        print(colored('[ERROR] ', 'red'), 'Error linking')
        md5s[out_dir + '/' + out_file + out_ext] = '0'
        save_md5()
        exit(error)
    else:
        print(colored('[INFO] ', 'green'), 'Linking successful')
        check_file_updated(out_dir + '/' + out_file + out_ext)
        save_md5()

def clean():
    if platform.system() == 'Windows':
        run_ps('Remove-Item ' + out_dir + '\\' + out_file + out_ext + ' -Force')
        print(colored('[LOG] ', 'yellow') ,'Cleaned ' + out_dir + '\\' + out_file + out_ext)
        run_ps('Remove-Item ' + obj_dir + ' -Recurse -Force')
        print(colored('[LOG] ', 'yellow') ,'Cleaned ' + obj_dir)
        run_ps('Remove-Item md5.txt')
        print(colored('[LOG] ', 'red') ,'Removed md5.txt')
    elif platform.system() == 'Linux':
        os.system('rm -rf ' + out_dir + '/' + out_file + out_ext)
        print(colored('[LOG] ', 'yellow') ,'Cleaned ' + out_dir + '/' + out_file + out_ext)
        os.system('rm -rf obj')
        print(colored('[LOG] ', 'yellow') ,'Cleaned ' + obj_dir)
        os.system('rm -rf md5.txt')
        print(colored('[LOG] ', 'red') ,'Removed md5.txt')
    else:
        print(colored('[ERROR] ', 'red'), 'Unsupported platform')
def check_mode():
    if len(os.sys.argv) == 1:
        return 'build'
    elif len(os.sys.argv) == 2:
        if os.sys.argv[1] == '--clean' or os.sys.argv[1] == '-c':
            return 'clean'
        elif os.sys.argv[1] == '--run' or os.sys.argv[1] == '-r':
            return 'run'
        elif os.sys.argv[1] == '--help' or os.sys.argv[1] == '-h':
            return 'help'
        elif os.sys.argv[1] == '--build' or os.sys.argv[1] == '-b':
            return 'build'
        elif os.sys.argv[1] == '--rebuild' or os.sys.argv[1] == '-rb':
            return 'rebuild'
        else:
            print(colored('[ERROR] ', 'red'), 'Unknown Command')
            exit(1)
    else:
        print(colored('[ERROR] ', 'red'), 'Too many arguments')


def usage():
    print(colored('[HELP] :', 'green'), 'Usage:')
    print(colored('[HELP] :', 'green'), 'To build the project:')
    print(colored('    python builder.py ', 'yellow'), colored('or ', 'grey'), colored('python builder.py --build', 'yellow'), colored('or ', 'grey'), colored('python builder.py -b', 'yellow'))
    print(colored('[HELP] :', 'green'), 'To clean the project:')
    print(colored('    python builder.py --clean', 'yellow'), colored('or ', 'grey'), colored('python builder.py -c', 'yellow'))
    print(colored('[HELP] :', 'green'), 'To run the project:')
    print(colored('    python builder.py --run', 'yellow'), colored('or ', 'grey'), colored('python builder.py -r', 'yellow'))
    print(colored('[HELP] :', 'green'), 'To rebuild the project:')
    print(colored('    python builder.py --rebuild', 'yellow'), colored('or ', 'grey'), colored('python builder.py -rb', 'yellow'))

def main():
    mode = check_mode()
    print(colored('[LOG] ', 'blue') ,'WORK MODE: ' + mode)
    if mode == 'build':
        load_md5()
        build_objects(src_dir, obj_dir)
        link()
    elif mode == 'clean':
        clean()
    elif mode == 'run':
        if out_type == 'dll':
            print(colored('[ERROR] ', 'red'), 'Cannot run DLL')
            exit(1)
        load_md5()
        build_objects(src_dir, obj_dir)
        link()
        print('=======PROGRAM OUTPUT========')
        if platform.system() == 'Windows':
            run_ps(out_dir + '/' + out_file + out_ext)
        elif platform.system() == 'Linux':
            os.system(out_dir + '/' + out_file + out_ext)
    elif mode == 'rebuild':
        clean()
        load_md5()
        build_objects(src_dir, obj_dir)
        link()
    elif mode == 'help':
        usage()
    else:
        print(colored('[ERROR] ', 'red'), 'Unknown Command')
        exit(1)

if __name__=='__main__':
    main()