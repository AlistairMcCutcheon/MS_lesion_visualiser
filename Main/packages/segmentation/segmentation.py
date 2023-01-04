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

        self.imgs_paths = []
        self.imgs_segmentations_paths = []
        self.sub_imgs_paths = []
        self.sub_imgs_segmentations_paths = []
        self.load_paths()
        
    def validate(self) -> None:
        if not self.dir_path.exists():
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), str(self.dir_path))
        if not (self.dir_path / self.get_path(FileType.IMG, 0)).exists():
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), str(self.dir_path / self.get_path(FileType.IMG, 0)))
        if not (self.dir_path / self.get_path(FileType.IMG_SEGMENTATION, 0)).exists():
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), str(self.dir_path / self.get_path(FileType.IMG_SEGMENTATION, 0)))

    def load_paths(self):
        self.imgs_paths.append(self.get_path(FileType.IMG, 0))
        self.imgs_segmentations_paths.append(self.get_path(FileType.IMG_SEGMENTATION, 0))
        for i in itertools.count():
            if self.index_has_no_imgs(i):
                break

            try:
                self.imgs_paths.append(self.get_path(FileType.IMG, i))
            except FileNotFoundError as e:
                raise InvalidSegmentationDirError(self.dir_path) from e

            try:
                self.imgs_segmentations_paths.append(self.get_path(FileType.IMG_SEGMENTATION, i))
            except FileNotFoundError as e:
                raise InvalidSegmentationDirError(self.dir_path) from e

            try:
                sub_img_path = self.get_path(FileType.SUB_IMG, i)
                sub_img_segmentation_path = self.get_path(FileType.SUB_IMG_SEGMENTATION, i)
            except FileNotFoundError as e:
                self.sub_imgs_paths.append(None)
                self.sub_imgs_segmentations_paths.append(None)
                logging.warning(e)
            else:
                self.sub_imgs_paths.append(sub_img_path)
                self.sub_imgs_segmentations_paths.append(sub_img_segmentation_path)

    def index_has_no_imgs(self, index) -> bool:
        img_path = Path(self.dir_path) / file_type_to_name(FileType.IMG, index)
        img_segmentation_path = Path(self.dir_path) / file_type_to_name(FileType.IMG_SEGMENTATION, index)
        return not img_path.exists() and not img_segmentation_path.exists()

    def get_path(self, file_type: FileType, index) -> str:
        path = Path(self.dir_path) / file_type_to_name(file_type, index)
        if not Path(path).exists():
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), str(path))
        return path
