import os, sys
import subprocess
import re

#print os.environ['http_proxy']
#print os.environ['HTTP_PROXY']
os.environ['http_proxy']=''
os.environ['HTTP_PROXY']=''

# Enable tcp service to allow non-root communication with docker daemon
#sudo service docker stop
#sudo docker --daemon=true -H tcp://127.0.0.1:2376
#sudo docker --daemon=true -H tcp://127.0.0.1:2376 -d --bip=172.17.42.1/16
DOCKER = ['docker', '-H', '127.0.0.1:2376']
#DOCKER = ['docker']
        

def docker_run_rm(container_name, image_name, *exec_command):
    docker_command = []  
    docker_command.extend(DOCKER)    
    docker_command.extend(['run', '--rm', '--name', container_name, image_name])
    docker_command.extend(exec_command)
    p = subprocess.Popen(docker_command,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out = p.stdout.read()
    print out
    err = p.stderr.read()
    print err
    return out

def docker_run(container_name, image_name, *exec_command):
    # TODO:  
    #if keep_live:
    #    docker_command.extend(['-t'])
    docker_command = []
    docker_command.extend(DOCKER)
    docker_command.extend(['run', '--name', container_name, image_name])
    docker_command.extend(exec_command)
    p = subprocess.Popen(docker_command,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out = p.stdout.read()
    print out
    err = p.stderr.read()
    print err 

def docker_rm(container_name, force=False):
    docker_command = []
    docker_command.extend(DOCKER)
    docker_command.extend(['rm'])
    docker_command.extend(['--force=' + str(force)])
    docker_command.extend([container_name])
    try:
        out = subprocess.check_output(docker_command)
    except subprocess.CalledProcessError as e:
        print "Status: FAIL", e.returncode, e.output
    else:
        return out

def docker_ps_a():
    docker_command = []
    docker_command.extend(DOCKER)
    docker_command.extend(['ps', '-a'])
    p = subprocess.Popen(docker_command,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out = p.stdout.read()
    print out
    err = p.stderr.read()
    print err     

def docker_images():
    docker_command = []
    docker_command.extend(DOCKER)
    docker_command.extend(['images'])
    out = subprocess.check_output(docker_command)
    #out = p.stdout.read()
    #print out
    #err = p.stderr.read()
    #print err 
    
    image_names = re.findall(r'^(.*?)\s', out, re.MULTILINE)
    image_names.pop(0)  # remove the 'REPOSITORY' column header from the list
    #print image_names
    return image_names
    
def docker_create(container_name, image_name, keep_live=False, shared_directory=None):
    docker_command = []
    docker_command.extend(DOCKER)
    docker_command.extend(['create'])
    if keep_live:
        docker_command.extend(['-t'])
    if shared_directory:
        docker_command.extend(['--volume=' + shared_directory + ':/shared_with_docker_host'])
    docker_command.extend(['--name', container_name, image_name])
    try:
        print docker_command
        out = subprocess.check_output(docker_command)
    except subprocess.CalledProcessError as e:
        print "Status: FAIL", e.returncode, e.output
        sys.exit(1)
    else:
        print out
        return out

def docker_start(container_name):
    docker_command = []
    docker_command.extend(DOCKER)
    docker_command.extend(['start', '--attach=false', container_name])
    try:
        out = subprocess.check_output(docker_command)
    except subprocess.CalledProcessError as e:
        print "Status: FAIL", e.returncode, e.output
        sys.exit(1)
    else:
        print out
        
def docker_stop(container_name):
    docker_command = []
    docker_command.extend(DOCKER)
    docker_command.extend(['stop', container_name])
    try:
        out = subprocess.check_output(docker_command)
    except subprocess.CalledProcessError as e:
        print "Status: FAIL", e.returncode, e.output
    else:
        print out    

def docker_exec(container_name, exec_command, *exec_command_arguments):
    docker_command = []
    docker_command.extend(DOCKER)
    docker_command.extend(['exec', container_name, exec_command])
    docker_command.extend(exec_command_arguments)
    print docker_command
    try:
        out = subprocess.check_output(docker_command)
    except subprocess.CalledProcessError as e:
        print "Status: FAIL", e.returncode, e.output
        sys.exit(1)
    else:
        return out 

if __name__ == '__main__':
    my_container_name = 'delme'
    #my_image_name = 'my_gcc_4_8_2_image:latest'
    my_image_name = 'ubuntu:14.04'
    
    #docker_ps_a()
    #docker_run_rm(my_container_name)
    #docker_ps_a()
    #docker_run(my_container_name)
    #docker_ps_a()
    docker_rm(my_container_name)
    #docker_ps_a()
    docker_create(my_container_name, my_image_name, keep_live=True)
    docker_start(my_container_name)
    #docker_ps_a()
    #docker_rm(my_container_name)
    #docker_ps_a()
    #docker_run_rm(my_container_name, my_image_name, ['ls', '-a'])
    #docker_run(my_container_name, my_image_name, ['ls', '-a'])
    #docker_ps_a()
    #docker_rm(my_container_name)
    #docker_ps_a()
    #image_names = docker_images()
    #out = docker_exec(my_container_name, 'gcc', '--version')
    out = docker_exec(my_container_name, 'ls')
    print out
    docker_stop(my_container_name)
    docker_rm(my_container_name)
    docker_ps_a()
    