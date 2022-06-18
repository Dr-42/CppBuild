import hashlib
import os

# Directories
bin_dir = 'bin'
obj_dir = 'obj'
src_dir = 'src'
libs = '-lm -lglfw -lGL -lGLEW -lassimp'

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
def check_file_updated(filename):
    with open(filename, 'rb') as f:
        contents = f.read()
    md5 = hashlib.md5(contents).hexdigest()
    if filename in md5s.keys():
        if md5s[filename] == md5:
            print('File not updated: ' + filename)
            return False
        else:
            print('File updated: ' + filename)
            if (not filename in md5s_to_update.keys()) and (filename in md5s.keys()):
                md5s_to_update[filename] = md5
            return True
    else:
        md5s[filename] = md5
        print('File added: ' + filename)
        return True

#generates the include command for filepath
def get_inc_cmd(filepath):
    cmd = ''
    cmds = []
    for inc in src_incs[filepath]:
        c = '-I' + incs[inc]
        if c not in cmds:
            cmds.append(c)
            cmd += ' -I' + incs[inc]
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
                incs[file] = root

#builds obj files for source_dir into obj_dir
def build_objects(source_dir, obj_dir):
    get_srcs(source_dir)
    for src in srcs:
        compile = False
        obj = srcs[src].replace('.cpp', '.o')
        obj = obj.replace(source_dir, obj_dir)
        objs[src] = obj
        parse_for_includes(srcs[src])
        if check_file_updated(srcs[src]):
            print('Compiling due to update to ' + srcs[src])
            compile = True
        for inc in src_incs[srcs[src]]:
            if check_file_updated(incs[inc] + '/' + inc):
                print('Compiling ' + srcs[src] + ' due to update to ' + incs[inc] + '/' + inc)
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

#parses file for includes
def parse_for_includes(file):
    with open(file, 'r') as f:
        for line in f:
            if line.startswith('#include "'):
                line = line.strip()
                line = line.replace('#include', '')
                line = line.replace('"', '')
                line = line.replace('\n', '')
                line = line.strip()

                if '/' in line:
                    line = line.split('/')[-1]

                if file not in src_incs.keys():
                    src_incs[file] = []
                if line not in src_incs[file]:
                    src_incs[file].append(line)
    
#links obj files into bin
def link():
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