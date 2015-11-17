#!/usr/bin/python2

import paramiko
import socket
import json
import sys

from subprocess import call, PIPE
from sys import argv
from random import randint
from time import sleep

from tempfile import mkdtemp
from os.path import dirname

def random_name():
    return str(randint(100000, 999999))

def run(command, fail = False):
    print("[+] local-run\t{0}".format(command))
    result = call(command, shell=True, stdout=PIPE, stderr=PIPE)
    if result != 0 and fail:
        raise Exception("Execution of '{0}' failed".format(command))
    return result

class Service:

    def __init__(self, name, config):
        self.name = name
        self.config = config

    def deploy(self, dirty_machine, team_machine):
        if self.name not in self.config:
            raise Exception("No information about {0} in config".format(self.name))

        self.__install_build_deps(dirty_machine)
        self.__pre_copy(dirty_machine)
        self.__add_user(team_machine)
        self.__install_run_deps(team_machine)
        self.__copy_files(dirty_machine, team_machine)
        self.__chmod_user(team_machine)
        self.__post_copy(dirty_machine, team_machine)

    def __add_user(self, machine):
        username, folder = self.config[self.name]["username"]
        machine.run('useradd -m {0}'.format(username))

    def __chmod_user(self, machine):
        username, folder = self.config[self.name]["username"]
        machine.run('chmod {0}:{0} -R /home/{1}'.format(username, folder))

    def __install_build_deps(self, machine):
        if "build_deps" not in self.config[self.name]:
            return
        build_deps = " ".join(self.config[self.name]["build_deps"])
        machine.run('apt-get update', True)
        machine.run('DEBIAN_FRONTEND=noninteractive apt-get install -y -q --force-yes {0}'.format(build_deps), True)

    def __install_run_deps(self, machine):
        if "run_deps" not in self.config[self.name]:
            return
        run_deps = " ".join(self.config[self.name]["run_deps"])
        machine.run('apt-get update', True)
        machine.run('DEBIAN_FRONTEND=noninteractive apt-get install -y -q --force-yes {0}'.format(run_deps), True)

    def __copy_files(self, from_machine, to_machine):
        files = self.config[self.name]["files"]
        tmp_directory = mkdtemp()
        for frm, to in files:
            run('mkdir -p {0}/{1}'.format(tmp_directory, dirname(frm)))
            from_machine.get('/root/ructfe-2015/{0}'.format(frm), '{0}/{1}'.format(tmp_directory, frm))
            to_machine.run('mkdir -p {0}'.format(dirname(to)))
            to_machine.put('{0}/{1}'.format(tmp_directory, frm), to)

    def __pre_copy(self, machine):
        if "precopy" not in self.config[self.name]:
            return
        script = self.config[self.name]["precopy"]
        machine.run('bash -x /root/ructfe-2015/{0}'.format(script), True)

    def __post_copy(self, from_machine, to_machine):
        if "postcopy" not in self.config[self.name]:
            return
        frm, to = self.config[self.name]["postcopy"]
        tmp_directory = mkdtemp()
        run('mkdir -p {0}/{1}'.format(tmp_directory, dirname(frm)))
        from_machine.get('/root/ructfe-2015/{0}'.format(frm), '{0}/{1}'.format(tmp_directory, frm))
        to_machine.run('mkdir -p {0}'.format(dirname(to)))
        to_machine.put('{0}/{1}'.format(tmp_directory, frm), to)
        to_machine.run('bash -x {0}'.format(to), True)
        to_machine.run('rm {0}'.format(to))


   
class Machine:

    def __init__(self, name, ip):
        self.key_filename = "/tmp/deploy-key-vbox"
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
        max_lap = 15
        while not_started:
            try:
                if lap > max_lap:
                    run("VBoxManage controlvm {0} setlinkstate1 off".format(self.name), True)
                    run("VBoxManage controlvm {0} setlinkstate1 on".format(self.name), True)
                    lap = 0
                    max_lap = 2
                sleep(1)
                not_started = False
                self.ssh_client.connect(ip, username="root", key_filename=self.key_filename)
                self.ssh_client.hostname = ip
            except (paramiko.ssh_exception.NoValidConnectionsError, socket.error):
                lap += 1
                not_started = True


    def start(self):
        # if self.__already_exists():
        #     raise Exception("Machine {0} is already exists".format(self.name))

        # run("VBoxManage clonevm {0} --mode all --name {1} --register".format(self.clean_name, self.name), True)
        # sleep(1)
        # run("VBoxManage modifyvm {0} --nic1 hostonly ".format(self.name), True)
        # run("VBoxManage modifyvm {0} --hostonlyadapter1 vboxnet0".format(self.name), True)
        # run("VBoxManage modifyvm {0} --macaddress1 auto".format(self.name), True)
        # run("VBoxManage startvm {0} --type headless".format(self.name), True)

        # self.__wait_for_ssh(self.clean_ip)

        # self.run("sed -i 's/{0}/{1}/' /etc/network/interfaces".format(self.clean_ip, self.ip))
        # self.run("sync")
        # sleep(1)
        # run('VBoxManage controlvm {0} reset'.format(self.name), True)

        self.__wait_for_ssh(self.ip)

    def stop(self):
        # run("VBoxManage controlvm {0} poweroff".format(self.name), True)
        # sleep(1)
        # run("VBoxManage unregistervm {0} --delete".format(self.name), True)
        pass

    def put(self, path_from, path_to):
        print("[+] remote-put\t{0}\t{1}\t{2}".format(self.ssh_client.hostname, path_from, path_to))
        run("scp -o StrictHostKeyChecking=no -o BatchMode=yes -i {3} -r {0} root@{1}:{2}".format(path_from, self.ssh_client.hostname, path_to, self.key_filename), True)

    def get(self, path_from, path_to):
        print("[+] remote-get\t{0}\t{1}\t{2}".format(self.ssh_client.hostname, path_from, path_to))
        run("scp -o StrictHostKeyChecking=no -o BatchMode=yes -i {3} -r root@{0}:{1} {2}".format(self.ssh_client.hostname, path_from, path_to, self.key_filename), True)

    def run(self, command, show_output=False):
        print("[+] remote-run\t{0}\t{1}".format(self.ssh_client.hostname, command))
        stdin, stdout, stderr = self.ssh_client.exec_command(command)
        if show_output:
            lines = map(lambda x: x.encode('ascii', 'ignore'), stdout.readlines())
            print('[stdout]\n {0}'.format("".join(lines).encode('ascii', 'ignore')))
            lines = map(lambda x: x.encode('ascii', 'ignore'), stderr.readlines())
            print('[stderr]\n {0}'.format("".join(lines).encode('ascii', 'ignore')))


class DirtyMachine(Machine):

    def __init__(self, name, ip):
        Machine.__init__(self, name, ip)

    def __clone_ructfe(self):
        self.put(self.key_filename, '/root/.ssh/id_rsa')
        self.run('chmod 600 /root/.ssh/id_rsa')
        self.run('apt-get install -y git', True)
        self.run('ssh-keyscan github.com >> /root/.ssh/known_hosts', True)
        self.run('git clone git@github.com:HackerDom/ructfe-2015.git /root/ructfe-2015', True)

    def __enter__(self):
        try:
            self.start()
            self.__clone_ructfe()
        except (KeyboardInterrupt, Exception) as e:
            self.stop()
            raise
        return self

    def __exit__(self, exit_type, exit_value, exit_traceback):
        self.stop()

class TeamMachine(Machine):

    def __init__(self, name, ip):
        Machine.__init__(self, name, ip)

    def __enter__(self):
        try:
            self.start()
        except (KeyboardInterrupt, Exception) as e:
            self.stop()
            raise
        return self

    def __exit__(self, exit_type, exit_value, exit_traceback):
        self.stop()

class NasaRasa(Service):

    def __init__(self, config):
        Service.__init__(self, "NasaRasa", config)

class MoL(Service):

    def __init__(self, config):
        Service.__init__(self, "MoL", config)

class TaX(Service):

    def __init__(self, config):
        Service.__init__(self, "TaX", config)

class HM(Service):

    def __init__(self, config):
        Service.__init__(self, "HM", config)

class Static(Service):

    def __init__(self, config):
        Service.__init__(self, "static", config)

class Electro(Service):

    def __init__(self, config):
        Service.__init__(self, "Electro", config)

class Bank(Service):

    def __init__(self, config):
        Service.__init__(self, "Bank", config)
  
def read_config(filename):
    with open(filename) as f:
        return json.load(f)

def main(argv):
    if len(argv) != 2:
        print("./deploy.py config.json")
        return 0

    config = read_config(argv[1])
    run('cp deploy-key /tmp/deploy-key-vbox', True)
    run('chmod 600 /tmp/deploy-key-vbox', True)
    with DirtyMachine("dirty-x64", "10.70.0.4") as dirty_machine, TeamMachine("team220-x64", "10.70.0.220") as team_machine:
        # services = [Static(config), NasaRasa(config), MoL(config), TaX(config), HM(config), Electro(config)]
        services = [Static(config), Bank(config)]
        for service in services:
            service.deploy(dirty_machine, team_machine)

        sys.stdin.read(1)

if __name__ == "__main__":
    main(argv)
