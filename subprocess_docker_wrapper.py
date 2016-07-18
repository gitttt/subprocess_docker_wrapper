import os, sys
import subprocess
import re
from docker import Client

#print os.environ['http_proxy']
#print os.environ['HTTP_PROXY']
os.environ['http_proxy']=''
os.environ['HTTP_PROXY']=''

# Enable tcp service to allow non-root communication with docker daemon
#sudo service docker stop
#sudo docker --daemon=true -H tcp://127.0.0.1:2376
DOCKER = ['docker', '-H', '127.0.0.1:2376']
#DOCKER = ['docker']

def docker_py_way():
    os.environ['DOCKER_API_VERSION']='1.18'
    
    # You may adapt the version to avoid "client and server don't have same version"
    # see http://stackoverflow.com/a/38261816/4480139
    docker_client = Client(base_url='tcp://127.0.0.1:2376', version='1.18')
    
    #docker_client = Client(base_url='unix://var/run/docker.sock')
    # You need to adapt permissons if a docker-py userland script wants to be able to connect
    
    """
    Volume declaration is done in two parts.
    Provide a list of mountpoints to the Client().create_container() method,
    and declare mappings in the host_config section.
    """
    
    my_volumes=['/shared_with_host']
    
    # I don't know yet why the dict way does not work
    my_shared_folder_mapping_dict = {
        '/tmp/shared_with_guest': {
            'bind': '/shared_with_host',
            'mode': 'rw'
        }
    }    
    my_host_config = docker_client.create_host_config(binds=my_shared_folder_mapping_dict)
    
    #my_shared_folder_mapping_list = ['/tmp/shared_with_guest:/shared_with_host:rw']
    #my_host_config = docker_client.create_host_config(binds=my_shared_folder_mapping_list)
    
    try:
        # create_container "creates a container that can then be .start()ed"
        my_container = docker_client.create_container(image='my_gcc_4_8_2_image:latest',
                                                      command='ls',
                                                      volumes=my_volumes,
                                                      host_config=my_host_config)
        
        # We need to start the container before we can send commands
        response = docker_client.start(container=my_container.get('Id'))
        print "response: %s" % response
        
        # Now that the container is started, we can send commands to it
        my_exec_id = docker_client.exec_create(my_container, 'ls /shared_with_host')
        return_string = docker_client.exec_start(my_exec_id)
        print "return_string: %s", return_string
        
        #print docker_client.containers(all=True)
        #try:  # sometimes the container is not stopped (yet), so this is necessary
            ##TODO: smarter way to check if container is still running
            #docker_client.stop(my_container)
        #except:
            #pass
        print "docker_client.containers(all=True): %s" % docker_client.containers(all=True)
        docker_client.wait(my_container)
        #print "docker_client.containers(all=True): %s" % docker_client.containers(all=True)
    except Exception as e:
        print e
        
    
    finally:
        #docker_client.remove_container(my_container, force=True)
        docker_client.remove_container(my_container, force=False)
        print "docker_client.containers(all=True): %s" % docker_client.containers(all=True)

        from subprocess import Popen, PIPE
        

def docker_run_rm(container_name, image_name, *exec_command):
    # TODO:  
    #if keep_live:
    #    docker_command.extend(['-t'])    
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
        out = subprocess.check_output(docker_command)
    except subprocess.CalledProcessError as e:
        print "Status: FAIL", e.returncode, e.output
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
    else:
        return out 

if __name__ == '__main__':
    my_container_name = 'delme'
    my_image_name = 'my_gcc_4_8_2_image:latest'
    
    #docker_ps_a()
    #docker_run_rm(my_container_name)
    #docker_ps_a()
    #docker_run(my_container_name)
    #docker_ps_a()
    #docker_rm(my_container_name)
    #docker_ps_a()
    docker_create(my_container_name, my_image_name, keep_live=True)
    #docker_start(my_container_name)
    #docker_ps_a()
    #docker_rm(my_container_name)
    #docker_ps_a()
    #docker_run_rm(my_container_name, my_image_name, ['ls', '-a'])
    #docker_run(my_container_name, my_image_name, ['ls', '-a'])
    #docker_ps_a()
    #docker_rm(my_container_name)
    #docker_ps_a()
    #image_names = docker_images()
    out = docker_exec(my_container_name, 'gcc', '--version')
    print out
    docker_rm(my_container_name)
    docker_ps_a()
    