import itertools
import errno
import os
from pathlib import Path
import logging
from packages.segmentation.file_types import FileType, file_type_to_name
import slicer
from slicer.util import MRMLNodeNotFoundException
from enum import Enum, auto


class View(Enum):
    STANDARD = 1
    SUB = auto()

def view_to_filetypes(view: View) -> tuple[FileType, FileType]:
    if view == View.STANDARD:
        return FileType.IMG, FileType.IMG_SEGMENTATION
    if view == View.SUB:
        return FileType.SUB_IMG, FileType.SUB_IMG_SEGMENTATION
    raise NotImplementedError(f"Unsupported enum value: {view}")


class InvalidSegmentationDirError(ValueError):
    def __init__(self, path: str) -> None:
        super().__init__(f"Not a valid segmentation directory: {path}")


class SegmentationDir:
    def __init__(self, dir_path: str) -> None:
        self._dir_path = Path(dir_path)
        try:
            self.validate()
        except FileNotFoundError as e:
            raise InvalidSegmentationDirError(self._dir_path) from e

        self.imgs_paths = {}
        self.imgs_segmentations_paths = {}
        self.sub_imgs_paths = {}
        self.sub_imgs_segmentations_paths = {}
        self.load_paths()

        self.view = View.STANDARD
        self.index = None
        
    def validate(self) -> None:
        if not self._dir_path.exists():
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), str(self._dir_path))
        if not (self._dir_path / self.get_path(FileType.IMG, 0)).exists():
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), str(self._dir_path / self.get_path(FileType.IMG, 0)))
        if not (self._dir_path / self.get_path(FileType.IMG_SEGMENTATION, 0)).exists():
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), str(self._dir_path / self.get_path(FileType.IMG_SEGMENTATION, 0)))

    def load_paths(self):
        self.imgs_paths[0] = self.get_path(FileType.IMG, 0)
        self.imgs_segmentations_paths[0] = self.get_path(FileType.IMG_SEGMENTATION, 0)
        for img_index, sub_img_index in zip(itertools.count(1), itertools.count(0)):
            if self.index_has_no_imgs(img_index):
                break

            try:
                img_path = self.get_path(FileType.IMG, img_index)
                img_segmentation_path = self.get_path(FileType.IMG_SEGMENTATION, img_index)
            except FileNotFoundError as e:
                raise InvalidSegmentationDirError(self._dir_path) from e
            else:
                self.imgs_paths[img_index] = img_path
                self.imgs_segmentations_paths[img_index] = img_segmentation_path

            try:
                self.sub_imgs_paths[sub_img_index] = self.get_path(FileType.SUB_IMG, sub_img_index)
                self.sub_imgs_segmentations_paths[sub_img_index] = self.get_path(FileType.SUB_IMG_SEGMENTATION, sub_img_index)
            except FileNotFoundError as e:
                logging.warning(e)

    def index_has_no_imgs(self, index) -> bool:
        img_path = Path(self._dir_path) / file_type_to_name(FileType.IMG, index)
        img_segmentation_path = Path(self._dir_path) / file_type_to_name(FileType.IMG_SEGMENTATION, index)
        return not img_path.exists() and not img_segmentation_path.exists()

    def index_is_valid_for_img(self, index):
        return index in self.imgs_paths and index in self.imgs_segmentations_paths

    def index_is_valid_for_sub_img(self, index):
        return index in self.sub_imgs_paths and index in self.sub_imgs_segmentations_paths

    def get_path(self, file_type: FileType, index) -> str:
        path = Path(self._dir_path) / file_type_to_name(file_type, index)
        if not Path(path).exists():
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), str(path))
        return str(path)

    def unload(self):
        def remove_node(search_pattern):
            try:
                node = slicer.util.getNode(search_pattern)
            except MRMLNodeNotFoundException:
                return
            slicer.mrmlScene.RemoveNode(node)

        for i in self.imgs_paths:
            remove_node(f"{file_type_to_name(FileType.IMG, i)}*")
        for i in self.imgs_segmentations_paths:
            remove_node(file_type_to_name(FileType.IMG_SEGMENTATION, i))
        for i in self.sub_imgs_paths:
            remove_node(f"{file_type_to_name(FileType.SUB_IMG, i)}*")
        for i in self.sub_imgs_segmentations_paths:
            remove_node(file_type_to_name(FileType.SUB_IMG_SEGMENTATION, i))


    def load_volume_node_if_not_exists(self, path, name, search_pattern):
        try:
            self.set_volume_node_to_visible(slicer.util.getNode(f"{search_pattern}*"))
        except MRMLNodeNotFoundException:
            slicer.util.loadVolume(
                path, 
                properties={
                    "name": name, 
                    "labelmap": False, 
                    "singleFile": True, 
                    "show": True
                }
            )

    def load_segmentation_node_if_not_exists(self, path, name, search_pattern):
        self.setSegmentationNodesToInvisible()
        try:
            slicer.util.getNode(f"{search_pattern}").SetDisplayVisibility(1)
        except MRMLNodeNotFoundException:
            slicer.util.loadSegmentation(path, properties={"name": name})


    def set_volume_node_to_visible(self, volume_node):
        appLogic = slicer.app.applicationLogic()
        selectionNode = appLogic.GetSelectionNode()
        selectionNode.SetActiveVolumeID(volume_node.GetID())
        appLogic.PropagateVolumeSelection()

    def setSegmentationNodesToInvisible(self):
        # Sets the visibility of the segmentation nodes to 0. It does not set the visibility of each segment to 0
        for i in range(slicer.mrmlScene.GetNumberOfNodesByClass('vtkMRMLSegmentationNode')):
            slicer.mrmlScene.GetNthNodeByClass(i, 'vtkMRMLSegmentationNode').SetDisplayVisibility(0)

    def load_index(self, view: View, index: int):

        volume_filetype, segmentation_filetype = view_to_filetypes(view)

        volume_file_path = self.get_path(volume_filetype, index)
        volume_name = file_type_to_name(volume_filetype, index)

        self.load_volume_node_if_not_exists(
            volume_file_path,
            volume_name,
            volume_name + "*"
        )

        segmentation_file_path = self.get_path(segmentation_filetype, index)
        segmentation_name = file_type_to_name(segmentation_filetype, index)

        self.load_segmentation_node_if_not_exists(
            segmentation_file_path,
            segmentation_name,
            segmentation_name,
        )

        self.view = view
        self.index = index

    @property
    def dir_path(self):
        return str(self._dir_path)

    @dir_path.setter
    def dir_path(self, dir_path):
        self._dir_path = Path(dir_path)

    
