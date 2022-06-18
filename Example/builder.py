import hashlib
import os

# Directories
bin_dir = 'bin'
obj_dir = 'obj'
src_dir = 'src'
libs = '-lm -lglfw -lGL -lGLEW -lassimp'

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

# Saves md5s to file
def save_md5():
    os.system('rm md5.txt && touch md5.txt')
    for file in md5s.keys():
        if file in md5s_to_update.keys():
            md5s[file] = md5s_to_update[file]
    with open('md5n.txt', 'w') as f:
        for key in md5s:
            f.write(key + ' ' + md5s[key] + '\n')
    os.system('rm md5.txt && mv md5n.txt md5.txt')

# Loads md5s from file
def load_md5():
    if not os.path.exists('md5.txt'):
        print('creating md5.txt')
        os.system('touch md5.txt')
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
            print('File not updated: ' + long_filename)
            return False
        else:
            print('File updated: ' + long_filename)
            if (not long_filename in md5s_to_update.keys()) and (long_filename in md5s.keys()):
                md5s_to_update[long_filename] = md5
            return True
    else:
        md5s[long_filename] = md5
        print('File added: ' + long_filename)
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
            if file.endswith('.cpp'):
                srcs[file] = os.path.join(root, file)
            if file.endswith('.h'):
                incs[file] = os.path.join(root, file)

#builds obj files for source_dir into obj_dir
def build_objects(source_dir, obj_dir):
    get_srcs(source_dir)
    if not os.path.exists(obj_dir):
        os.system('mkdir ' + obj_dir)
    for src in srcs:
        compile = False
        obj = srcs[src].split('/')[-1].replace('.cpp', '.o')
        obj = obj_dir + '/' + obj
        objs[src] = obj
        parse_for_includes(srcs[src])
        if check_file_updated(srcs[src]):
            print('Compiling due to update to ' + srcs[src])
            compile = True
        if srcs[src] in src_incs.keys():
            for inc in src_incs[srcs[src]]:
                incfile = inc.split('/')[-1]
                if check_file_updated(incs[incfile]):
                    print('Compiling ' + srcs[src] + ' due to update to ' + incs[incfile])
                    compile = True
        if compile:
            compile_obj(srcs[src], obj)

compiled_obj = False
#compiles filepath.cpp to obj
def compile_obj(filepath, obj):
    cmd = 'g++ -c -o ' + obj + ' ' + filepath + get_inc_cmd(filepath)
    print(cmd)
    os.system('pwd')
    os.system(cmd)
    global compiled_obj
    compiled_obj = True

#links obj files into bin
def link():
    if not os.path.exists(bin_dir):
        os.system('mkdir ' + bin_dir)
    if not compiled_obj:
        print('Nothing to be compiled')
        return
    objtot = ''
    i = 0
    for obj in objs:
        objtot += ' ' + objs[obj]
        i += 1
    cmd = 'g++ -o ' + bin_dir + '/' + 'main ' + objtot + ' ' + libs
    print(cmd)
    os.system(cmd)

def clean():
    os.system('rm -rf bin/*')
    os.system('rm -rf obj/*.o')
    os.system('rm -rf md5.txt')

def check_mode():
    if len(os.sys.argv) == 1:
        return 'build'
    elif len(os.sys.argv) == 2:
        if os.sys.argv[1] == 'clean':
            return 'clean'
        elif os.sys.argv[1] == 'run':
            return 'run'
        elif os.sys.argv[1] == 'help':
            return 'help'
        else:
            print('Unknown Command')
            exit(1)
    else:
        print('Too many arguments')


def usage():
    print('Usage:')
    print('  builder.py')
    print('  builder.py clean')
    print('  builder.py run')


def main():
    mode = check_mode()
    print('DEBUG: ' + mode)
    if mode == 'build':
        load_md5()
        build_objects(src_dir, obj_dir)
        link()
        save_md5()
    elif mode == 'clean':
        clean()
    elif mode == 'run':
        load_md5()
        build_objects(src_dir, obj_dir)
        link()
        print('=======PROGRAM OUTPUT========')
        os.system(bin_dir + '/' + 'main')
        save_md5()
    elif mode == 'help':
        usage()
    else:
        print('Unknown Command')
        exit(1)

if __name__=='__main__':
    main()
