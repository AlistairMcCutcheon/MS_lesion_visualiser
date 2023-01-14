import itertools
import errno
import os
from pathlib import Path
import logging
from packages.segmentation.file_types import FileType, file_type_to_name


class InvalidSegmentationDirError(ValueError):
    def __init__(self, path: str) -> None:
        super().__init__(f"Not a valid segmentation directory: {path}")


class SegmentationDir:
    def __init__(self, dir_path: str) -> None:
        self.dir_path = Path(dir_path)
        try:
            self.validate()
        except FileNotFoundError as e:
            raise InvalidSegmentationDirError(self.dir_path) from e

        self.imgs_paths = {}
        self.imgs_segmentations_paths = {}
        self.sub_imgs_paths = {}
        self.sub_imgs_segmentations_paths = {}
        self.load_paths()
        
    def validate(self) -> None:
        if not self.dir_path.exists():
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), str(self.dir_path))
        if not (self.dir_path / self.get_path(FileType.IMG, 0)).exists():
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), str(self.dir_path / self.get_path(FileType.IMG, 0)))
        if not (self.dir_path / self.get_path(FileType.IMG_SEGMENTATION, 0)).exists():
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), str(self.dir_path / self.get_path(FileType.IMG_SEGMENTATION, 0)))

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
                raise InvalidSegmentationDirError(self.dir_path) from e
            else:
                self.imgs_paths[img_index] = img_path
                self.imgs_segmentations_paths[img_index] = img_segmentation_path

            try:
                self.sub_imgs_paths[sub_img_index] = self.get_path(FileType.SUB_IMG, sub_img_index)
                self.sub_imgs_segmentations_paths[sub_img_index] = self.get_path(FileType.SUB_IMG_SEGMENTATION, sub_img_index)
            except FileNotFoundError as e:
                logging.warning(e)

    def index_has_no_imgs(self, index) -> bool:
        img_path = Path(self.dir_path) / file_type_to_name(FileType.IMG, index)
        img_segmentation_path = Path(self.dir_path) / file_type_to_name(FileType.IMG_SEGMENTATION, index)
        return not img_path.exists() and not img_segmentation_path.exists()

    def index_is_valid_for_img(self, index):
        return index in self.imgs_paths and index in self.imgs_segmentations_paths

    def index_is_valid_for_sub_img(self, index):
        print(self.sub_imgs_paths)
        print(self.sub_imgs_segmentations_paths)
        return index in self.sub_imgs_paths and index in self.sub_imgs_segmentations_paths

    def get_path(self, file_type: FileType, index) -> str:
        path = Path(self.dir_path) / file_type_to_name(file_type, index)
        if not Path(path).exists():
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), str(path))
        return path
