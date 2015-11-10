#!/usr/bin/python2

import paramiko
import socket

from subprocess import call, PIPE
from sys import argv
from random import randint
from time import sleep

def random_name():
    return str(randint(100000, 999999))

def run(command, fail = False):
    print("[+] local-run\t{0}".format(command))
    result = call(command, shell=True, stdout=PIPE, stderr=PIPE)
    if result != 0 and fail:
        raise Exception("Execution of '{0}' failed".format(command))
    return result

class Service:

    def __init__(self, name):
        pass

class NasaRasa(Service):

    def __init__(self):
        Service.__init__(self, "NasaRasa")

class Machine:

    def __init__(self, name, ip):
        self.key_filename = "deploy-key"
        self.clean_name = "clean" # name of clean machine in vbox
        self.clean_ip = "10.70.0.2" # its ip
        self.name = name
        self.ip = ip

    def __already_exists(self):
        result = run("VBoxManage list vms | grep {0}".format(self.name))
        return result == 0

    def __wait_for_ssh(self, ip):
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        not_started = True
        lap = 0
        while not_started:
            try:
                if lap > 15:
                    run("VBoxManage controlvm {0} reset".format(self.name))
                    lap = 0
                sleep(1)
                not_started = False
                self.ssh_client.connect(ip, username="root", key_filename=self.key_filename)
                self.ssh_client.hostname = ip
                self.sftp_client = self.ssh_client.open_sftp()
            except (paramiko.ssh_exception.NoValidConnectionsError, socket.error):
                lap += 1
                not_started = True


    def start(self):
        if self.__already_exists():
            raise Exception("Machine {0} is already exists".format(self.name))

        run("VBoxManage clonevm {0} --mode all --name {1} --register".format(self.clean_name, self.name), True)
        sleep(1)
        run("VBoxManage modifyvm {0} --nic1 hostonly ".format(self.name), True)
        run("VBoxManage modifyvm {0} --hostonlyadapter1 vboxnet0".format(self.name), True)
        run("VBoxManage modifyvm {0} --macaddress1 auto".format(self.name), True)
        run("VBoxManage startvm {0} --type headless".format(self.name), True)

        self.__wait_for_ssh(self.clean_ip)

        self.run("sed -i 's/{0}/{1}/' /etc/network/interfaces".format(self.clean_ip, self.ip))
        self.run("sync")
        sleep(1)
        run('VBoxManage controlvm {0} reset'.format(self.name), True)

        self.__wait_for_ssh(self.ip)

    def stop(self):
        run("VBoxManage controlvm {0} poweroff".format(self.name), True)
        sleep(1)
        run("VBoxManage unregistervm {0} --delete".format(self.name), True)

    def copy(self, path_from, path_to):
        print("[+] remote-copy\t{0}\t{1}\t{2}".format(self.ssh_client.hostname, path_from, path_to))
        return self.sftp_client.put(path_from, path_to)

    def mkdir(self, path, mode=0777):
        return self.sftp_client.mkdir(path)

    def chmod(self, path, mode):
        return self.sftp_client.chmod(path, mode)

    def run(self, command):
        print("[+] remote-run\t{0}\t{1}".format(self.ssh_client.hostname, command))
        return self.ssh_client.exec_command(command)

class DirtyMachine(Machine):

    def __init__(self):
        Machine.__init__(self, random_name(), "10.70.0.3")

    def __clone_ructfe(self):
        self.copy('deploy-key', '/root/.ssh/id_rsa')
        self.chmod('/root/.ssh/id_rsa', 0600)
        _, stdout, stderr = self.run('ssh-keyscan github.com >> /root/.ssh/known_hosts')
        print(stdout.readlines())
        print(stderr.readlines())
        _, stdout, stderr = self.run('git clone git@github.com:HackerDom/ructfe-2015.git /root/ructfe-2015')
        print(stdout.readlines())
        print(stderr.readlines())

    def __enter__(self):
        try:
            self.start()
            self.__clone_ructfe()
        except (KeyboardInterrupt, Exception) as e:
            self.stop()
            raise

    def __exit__(self, exit_type, exit_value, exit_traceback):
        self.stop()

def main(argv):
    with DirtyMachine() as dirty_machine:
        services = [NasaRasa()]

if __name__ == "__main__":
    main(argv)
