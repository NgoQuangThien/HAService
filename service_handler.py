import logging
import os
import subprocess
import threading
import time
from ulti import read_file
from ulti import write_file


class ServiceHandler:
    def __init__(self, service_name):
        self.service_name = service_name
        self.cmd = "systemctl is-active " + service_name
        self.required_state = frozenset(['activating', 'reloading'])
        self.logger = logging.getLogger('sync')
        self.old_state = str()
        self.is_changed = False
        self.last_reload_time = 0.0
        write_file("/tmp/{service_name}.lock".format(service_name=self.service_name), "0")

    def service_hander(self):
        while True:
            current_state = os.popen(self.cmd).read().strip()
            if current_state != self.old_state:
                self.old_state = current_state
                if current_state in self.required_state:
                    if read_file("/tmp/{service_name}.lock".format(service_name=self.service_name)) == "0":
                        write_file("/tmp/{service_name}.lock".format(service_name=self.service_name), "1")
                        self.is_changed = True
                        time.sleep(3)
                        write_file("/tmp/{service_name}.lock".format(service_name=self.service_name), "0")

    def start(self):
        service_handler_thread = threading.Thread(target=self.service_hander, daemon=True)
        service_handler_thread.start()

    def validate_config(self):
        cmd = "nginx -t"
        result = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if "test failed" in result.stderr.read().decode('utf-8'):
            return False
        return True

    def remote_validate_config(self, server_name):
        sub_cmd = "nginx -t"
        cmd = "ssh root@{server_name} '{sub_cmd}'".format(server_name=server_name, sub_cmd=sub_cmd)
        result = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if "test failed" in result.stderr.read().decode('utf-8'):
            return False
        return True

    def remote_reload_service(self, server_name):
        sub_cmd = "echo 1 > /tmp/{service_name}.lock && systemctl reload {service_name}".format(service_name=self.service_name)
        cmd = "ssh root@{server_name} '{sub_cmd}'".format(server_name=server_name, sub_cmd=sub_cmd)
        result = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.stdout.read().decode('utf-8') == "" and result.stderr.read().decode('utf-8') == "":
            return True
        else:
            return False
