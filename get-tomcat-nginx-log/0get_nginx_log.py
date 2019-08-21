import subprocess
import socket
import datetime
import os
import ctypes
import platform

NO_NGINX = 0
NO_NGINX_CONF = 1
NO_NGINX_LOG = 2
SUCCESS = 6


def check_memory(path, style='M'):
    i = 0
    for dirpath, _, filename in os.walk(path):
        for ii in filename:
            i += os.path.getsize(os.path.join(dirpath, ii))
    memory = i / 1024. / 1024. / 1024.
    return memory


def get_free_space(folder):
    """ Return folder/drive free space (in bytes)
    """
    if platform.system() == 'Windows':
        free_bytes = ctypes.c_ulonglong(0)
        ctypes.windll.kernel32.GetDiskFreeSpaceExW(
            ctypes.c_wchar_p(folder), None, None, ctypes.pointer(free_bytes))
        return free_bytes.value/1024/1024/1024
    else:
        st = os.statvfs(folder)
        return st.f_bavail * st.f_frsize/1024/1024/1024.


def get_access_path():
    response_code = 0
    conf_path = ''
    log_path = ''
    log_path_tmp = ''
    process_tmp = []
    # prefix_path_index = 0
    tmp1 = subprocess.Popen(['ps -efw'], stdout=subprocess.PIPE, shell=True)
    tmp2 = subprocess.Popen(
        ['grep nginx'], stdin=tmp1.stdout, stdout=subprocess.PIPE, shell=True)
    ps_tmp = tmp2.stdout.read().decode()
    lines = ps_tmp.split('\n')
    for line in lines:
        if 'master process' in line:
            process_tmp = line.split()
            # prefix_path_index = process_tmp.index('process') + 1
            break
    if process_tmp == []:
        response_code = NO_NGINX
        return response_code, conf_path, log_path
    pid = process_tmp[1]
    tmp5 = subprocess.Popen(['ls -l /proc/' + pid + "/exe"], stdout=subprocess.PIPE, shell=True)
    proc_tmp = tmp5.stdout.read().decode()
    nginx_path = proc_tmp.split()[-1]
    prefix_path = nginx_path.split('sbin')[0]
    find_sp = subprocess.Popen(
        ['find ' + prefix_path + ' -name nginx.conf'], stdout=subprocess.PIPE, shell=True)
    conf_path = find_sp.stdout.read().decode().strip('\n')
    print("conf_path", conf_path)
    if conf_path == '':
        response_code = NO_NGINX_CONF
        return response_code, conf_path, log_path
    tmp3 = subprocess.Popen(['cat ' + conf_path],
                            stdout=subprocess.PIPE, shell=True)
    tmp4 = subprocess.Popen(
        ['grep access.log'], stdin=tmp3.stdout, stdout=subprocess.PIPE, shell=True)
    cat_res = tmp4.stdout.read().decode().split('\n')
    if cat_res == '':
        response_code = NO_NGINX_LOG
        return response_code, conf_path, log_path
    # cat_res ='''
    #     access_log logs/access.log  main buffer=128k flush=5s;
    #     access_log logs/access_for_big_data.log  bigData buffer=128k flush=5s;

    # '''
    # conf_path = "/opt/huawei/openred/nginx/conf/nginx.conf"
    for line in cat_res:
        if "main" in line:
            log_path_tmp = line.split()[1]
            break
    print("log_path_tmp", log_path_tmp)
    # print(cat_res)
    # for i in cat_res:
    #     if len(i) > 2:
    #         log_path_tmp = re.match(r'^(\S*)\/(access\.log)', i)
    #         if log_path_tmp != None:
    #             log_path = log_path_tmp.group(0)
    # print(log_path)
    if log_path_tmp == '':
        response_code = NO_NGINX_LOG
        return response_code, conf_path, log_path
    if log_path_tmp[0] == '/':
        log_path = log_path_tmp
    else:
        log_path = conf_path.replace("conf/nginx.conf", log_path_tmp)
    response_code = SUCCESS
    return response_code, conf_path, log_path

def cp_file(src_path, dir_path):
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    ip = ip.replace('.', '-')
    cmd = ['cp', src_path, dir_path]
    subprocess.Popen(cmd, stdout=subprocess.PIPE)

def write_log(content):
    with open("/tmp/get-logs-soc.txt", 'a') as f:
        f.write(content)
        f.write('\n')
        print(content)

if __name__ == "__main__":
    write_log("[INFO] BEGIN!!!!!!")
    response, conf_path, log_path = get_access_path()
    print(log_path)
    print(conf_path)
    if response == 6:
        free_space = get_free_space('/tmp')
        file_size = check_memory(log_path)
        if free_space > file_size:
            file_path = '/tmp/nginx_proof'
            tar_file = '/tmp/nginx_proof.tar.gz'
            if not os.path.exists(file_path):
                os.makedirs(file_path)
            cp_file(conf_path,file_path)
            cp_file(log_path,file_path)
            os.system("tar czf "+ tar_file + ' -C ' + file_path + ' .')
        else:
            write_log("[ERROR] Free spcace is limited!\n[INFO] free space: {free_space} \n[INFO] files_size:{file_size}".format(free_space=free_space, file_size=file_size))
    else:
        write_log("[ERROR]Fail to find log")
    print('FINISH!')
