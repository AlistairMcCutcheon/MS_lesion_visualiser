import os
import shutil

class TempDir:
    def __init__(self, path) -> None:
        self.path = path

    def __enter__(self):
        os.mkdir(self.path)
        return self.path

    def __exit__(self, exc_type, exc_value, traceback):
        shutil.rmtree(self.path)