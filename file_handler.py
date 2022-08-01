import pyinotify
from file_processor import ProcessTransientFile


class FileHandler:
    def __init__(self, conf):
        self.service_name = conf['name']
        self.paths = conf['paths']
        self.exclude = conf['exclude']
        self.node_peer = conf['node_peer']

        self.wm = pyinotify.WatchManager()
        self.mask = pyinotify.ALL_EVENTS
        self.process_transient_file = ProcessTransientFile(self.service_name, self.paths, self.exclude, self.node_peer)
        self.notifier = pyinotify.ThreadedNotifier(self.wm, self.process_transient_file)

    def start(self):
        for path in self.paths:
            self.wm.add_watch(path, self.mask, rec=True, auto_add=True)
        self.notifier.start()

    def stop(self):
        pass

    def list_watch(self):
        pass
