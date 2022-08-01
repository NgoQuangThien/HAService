import pyinotify
import logging
import subprocess


file_state = frozenset(['IN_MODIFY', 'IN_MOVED_TO', 'IN_MOVED_FROM', 'IN_CREATE', 'IN_DELETE', 'IN_DELETE_SELF',
                        'IN_MODIFY|IN_ISDIR', 'IN_MOVED_TO|IN_ISDIR', 'IN_MOVED_FROM|IN_ISDIR',
                        'IN_CREATE|IN_ISDIR', 'IN_DELETE|IN_ISDIR', 'IN_DELETE_SELF|IN_ISDIR'])


class ProcessTransientFile(pyinotify.ProcessEvent):
    def __init__(self, service_name, paths, exclude, domain, **kargs):
        super().__init__(**kargs)
        self.service_name = service_name
        self.paths = paths
        self.exclude = exclude
        self.domain = domain
        self.logger = logging.getLogger('sync')

    def check_file(self, file_name):
        if self.exclude:
            real_exclude = list()
            for path in self.paths:
                if path.endswith('/'):
                    for item in self.exclude:
                        real_exclude.append(path + item)
            if file_name in real_exclude:
                return False
        elif file_name.endswith('.swp'):
            return False
        elif file_name.endswith('.swpx'):
            return False
        elif file_name.endswith('~'):
            return False
        return True

    def generate_rsync_command(self):
        rsync_command = str()
        i = 0
        for path in self.paths:
            rsync_command += '/usr/bin/rsync -azq --delete --backup --backup-dir=/backup/{0} '.format(self.service_name)
            for ignore_file in self.exclude:
                rsync_command += '--exclude="{0}" '.format(ignore_file)
            rsync_command += path + ' ' + 'root@{0}:'.format(self.domain) + path
            if i < len(self.paths) - 1:
                rsync_command += ' && '
                i += 1
        return rsync_command

    def process_default(self, event):
        if event.maskname in file_state and self.check_file(event.pathname):
            rsync_command = self.generate_rsync_command()
            self.logger.info("File configuration changed, executing rsync command.")
            result = subprocess.Popen(rsync_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.stdout.read().decode('utf-8') == "" and result.stderr.read().decode('utf-8') == "":
                self.logger.info("Rsync command executed successfully.")
            else:
                self.logger.error("Rsync command failed.")
