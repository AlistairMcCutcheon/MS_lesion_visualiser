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

class SetParameters:
    def __init__(self, parameter_node) -> None:
        self.parameter_node = parameter_node
        

    def __enter__(self):
        self.modifier = self.parameter_node.StartModify()
        return self.parameter_node

    def __exit__(self, exc_type, exc_value, traceback):
        self.parameter_node.EndModify(self.modifier)

class BlockMethod:
    def __init__(self, class_instance, method_name) -> None:
        self.class_instance = class_instance
        self.method_name = method_name

    def do_nothing_method(self):
        pass

    def __enter__(self):
        
        self.method = getattr(self.class_instance, self.method_name)
        setattr(self.class_instance, self.method_name, self.do_nothing_method)

    def __exit__(self, exc_type, exc_value, traceback):
        setattr(self.class_instance, self.method_name, self.method)