# -*- coding: UTF-8 -*-

import subprocess
import socket
import datetime
import os
import ctypes
import platform

NO_TOMCAT = 0
NO_TOMCAT_CONF = 1
NO_TOMCAT_LOG = 2
SUCCESS = 6

file_names = []


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


def get_nday_list(n):
    before_n_days = []
    for i in range(1, n + 1)[::-1]:
        before_n_days.append(
            str(datetime.date.today() - datetime.timedelta(days=i)))
    return before_n_days


def get_base_path():
    response_code = 0
    base_path = ''
    base_path_tmp = ''
    # prefix_path_index = 0
    tmp1 = subprocess.Popen(['ps -efw'], stdout=subprocess.PIPE, shell=True)
    tmp2 = subprocess.Popen(
        ['grep java'], stdin=tmp1.stdout, stdout=subprocess.PIPE, shell=True)
    tmp3 = subprocess.Popen(
        ['grep Dcatalina.base'], stdin=tmp2.stdout, stdout=subprocess.PIPE, shell=True)
    ps_tmp = tmp3.stdout.read().decode()
    lines = ps_tmp.split('\n')
    if len(lines) < 2:
        response_code = NO_TOMCAT
        return response_code, base_path
    for line in lines:
        if 'Dcatalina.base' in line:
            base_path_tmp = line.split()
            break
    if base_path_tmp == '':
        response_code = NO_TOMCAT_CONF
        return response_code, base_path
    for section in base_path_tmp:
        if "Dcatalina.base" in section:
            base_path = section.split('=')[-1]
            # prefix_path_index = process_tmp.index('process') + 1
            break
    if base_path == '':
        response_code = NO_TOMCAT_CONF
        return response_code, base_path
    response_code = SUCCESS
    return response_code, base_path


def get_log_file_path(base_path):
    '''
    get the path of every log!
    '''
    log_paths = ['' for _ in range(6)]
    conf_tmp1 = subprocess.Popen(
        ['cat ' + base_path + '/conf/logging.properties'], stdout=subprocess.PIPE, shell=True)
    conf_tmp2 = subprocess.Popen(
        ['grep directory'], stdin=conf_tmp1.stdout,        stdout=subprocess.PIPE, shell=True)
    tmp_log_path_conf = conf_tmp2.stdout.read().decode()
    for line in tmp_log_path_conf.split('\n'):
        path_tmp = ''
        if '1catalina' in line:
            path_tmp = line.split('=')[-1].strip()
            if '${catalina.base}' in path_tmp:
                path_tmp = path_tmp.replace('${catalina.base}', base_path)
            log_paths[0] = path_tmp
            log_paths[1] = path_tmp
        elif '2localhost' in line:
            path_tmp = line.split('=')[-1].strip()
            if '${catalina.base}' in path_tmp:
                path_tmp = path_tmp.replace('${catalina.base}', base_path)
            log_paths[2] = path_tmp
        elif '3manager' in line:
            path_tmp = line.split('=')[-1].strip()
            if '${catalina.base}' in path_tmp:
                path_tmp = path_tmp.replace('${catalina.base}', base_path)
            log_paths[3] = path_tmp
        elif '4host-manager' in line:
            path_tmp = line.split('=')[-1].strip()
            if '${catalina.base}' in path_tmp:
                path_tmp = path_tmp.replace('${catalina.base}', base_path)
            log_paths[4] = path_tmp

    conf_tmp3 = subprocess.Popen(
        ['cat ' + base_path + '/conf/server.xml'], stdout=subprocess.PIPE, shell=True)
    conf_tmp4 = subprocess.Popen(
        ['grep AccessLogValve'], stdin=conf_tmp3.stdout, stdout=subprocess.PIPE, shell=True)
    tmp_log_path_conf = conf_tmp4.stdout.read().decode()
    for line in tmp_log_path_conf.split():
        if 'directory' in line:
            path_tmp = line.split('=')[-1].strip('\"').strip('\'')
            if path_tmp[0] != '/':
                if '${catalina.base}' in path_tmp:
                    path_tmp = path_tmp.replace('${catalina.base}', base_path)
                else:
                    path_tmp = base_path + '/' + path_tmp
            else:
                path_tmp = path_tmp
            log_paths[5] = path_tmp
            break

    return log_paths


def cp_file(src_path, dir_path):
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    ip = ip.replace('.', '-')
    cmd = ['cp', src_path, dir_path]
    subprocess.Popen(cmd, stdout=subprocess.PIPE)


def write_to_txt(filename, data):
    with open(filename, 'w') as f:
        for line in data:
            f.write(line + '\n')


def write_log(content):
    with open("/tmp/get-logs-soc.txt", 'a') as f:
        f.write(content)
        f.write('\n')
        print(content)


if __name__ == "__main__":
    write_log("[INFO] BEGIN!!!!!!")
    # get base path of tomcat or catalina and copy files except temp and logs
    response, base_path = get_base_path()
    write_log('[INFO]responese code:{response} \n[INFO]catalina root path:{base_path}'.format(response=response, base_path=base_path))
    if response == 6:
        free_space = get_free_space('/tmp')
        file_size = check_memory(base_path)
        if free_space > file_size:
            file_path = '/tmp/tomcat_proof'
            if not os.path.exists(file_path):
                os.makedirs(file_path)
            os.system('cp -r ' + base_path + '/* ' + file_path)
            os.system('rm -rf ' + file_path + 'temp')
            os.system('rm -rf ' + file_path + 'logs/*')
            write_log("[INFO] Finish to copy base path!")
            # get the path of each kind of log file and return the list of all logs
            log_paths = get_log_file_path(base_path)
            tmp_log_path = file_path + '/logs'
            file_list = []
            for i in log_paths:
                file_list = file_list + os.listdir(i)
            file_list = list(set(file_list))
            write_to_txt(tmp_log_path + '/file-list.txt', file_list)

            # get filenames of each kind of logs by date
            date_list = get_nday_list(2)
            for date in date_list:
                file_names.append(log_paths[0] + "/catalina.out")
                file_names.append(log_paths[1] + "/catalina." + date + '*')
                file_names.append(log_paths[2] + "/localhost." + date + '*')
                file_names.append(log_paths[3] + "/manager." + date + '*')
                file_names.append(log_paths[4] + "/host-manager." + date + '*')
                file_names.append(log_paths[5] + "/localhost_access_log." + date + '*')
            if not os.path.exists(tmp_log_path):
                os.makedirs(tmp_log_path)
            # begin copy the log files
            for file_name in file_names:
                if os.path.exists(file_name):
                    cp_file(file_name, tmp_log_path)
                else:
                    print("CAN NOT FIND ----"+file_name)
            write_log("[INFO] Finish to copy logs!")
            file_path = '/tmp/tomcat_proof'
            tar_file = '/tmp/tomcat_proof.tar.gz'
            os.system("tar czf " + tar_file + ' -C ' + file_path + ' .')
            write_log("[INFO] Finish to tar!")
        else:
            write_log("[ERROR] Free spcace is limited!\n[INFO] free space: {free_space} \n[INFO] files_size:{file_size}".format(free_space=free_space, file_size=file_size))
    else:
        write_log("[ERROR]Fail to find log")
    print("FINISH!!")
