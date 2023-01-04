import itertools
import errno
import os
from pathlib import Path
import logging

class SegmentationDirFileNames:
    @classmethod
    def img(cls, index: int) -> str:
        return f"img_{index}.nii.gz"

    @classmethod
    def img_segmentation(cls, index: int) -> str:
        return f"img_{index}_segmentation.nii.gz"

    @classmethod
    def sub_img(cls, index: int) -> str:
        return f"img_sub_{index}.nii.gz"

    @classmethod
    def sub_img_segmentation(cls, index: int) -> str:
        return f"img_sub_{index}_segmentation.nii.gz"


class InvalidSegmentationDirError(ValueError):
    def __init__(self, path: str) -> None:
        super().__init__(f"Not a valid segmentation directory: {path}")

class SegmentationDir:
    def __init__(self, dir_path: str) -> None:
        try:
            SegmentationDir.validate(Path(dir_path))
        except FileNotFoundError as e:
            raise InvalidSegmentationDirError(dir_path) from e

        self.dir_path = Path(dir_path)
        self.imgs = []
        self.imgs_segmentations = []
        self.sub_imgs = []
        self.sub_imgs_segmentations = []
        self.load_imgs_and_segmentations()
        self.load_sub_imgs_and_sub_segmentations()
        
    @staticmethod
    def validate(dir_path: Path) -> None:
        if not dir_path.exists():
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), str(dir_path))
        if not (dir_path / SegmentationDirFileNames.img(0)).exists():
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), str(dir_path / SegmentationDirFileNames.img(0)))
        if not (dir_path / SegmentationDirFileNames.img_segmentation(0)).exists():
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), str(dir_path / SegmentationDirFileNames.img_segmentation(0)))

    # def load(self):
    #     self.load_next_img_and_segmentation()
    #     for i in itertools.count():
    #         self.load_next_img_and_segmentation()
    #         self.load_next_sub_img_and_sub_segmentation()

    def load_imgs_and_segmentations(self):
        for i in itertools.count():
            img_file_path = self.dir_path / SegmentationDirFileNames.img(i)
            img_segmentation_file_path = self.dir_path / SegmentationDirFileNames.img_segmentation(i)

            if not img_file_path.exists() and not img_segmentation_file_path.exists():
                break

            try: 
                self.validate_img_segmentation_pair(img_file_path, img_segmentation_file_path)
            except FileNotFoundError as e:
                raise InvalidSegmentationDirError(self.dir_path) from e

            self.imgs.append(img_file_path)
            self.imgs_segmentations.append(img_segmentation_file_path)

    def load_sub_imgs_and_sub_segmentations(self):
        for i in itertools.count():
            img_file_path = self.dir_path / SegmentationDirFileNames.sub_img(i)
            sub_img_segmentation_file_path = self.dir_path / SegmentationDirFileNames.sub_img_segmentation(i)
            if not img_file_path.exists() and not sub_img_segmentation_file_path.exists():
                break

            try: 
                self.validate_img_segmentation_pair(img_file_path, sub_img_segmentation_file_path)
            except FileNotFoundError as e:
                raise InvalidSegmentationDirError(self.dir_path) from e

            self.sub_imgs.append(img_file_path)
            self.sub_imgs_segmentations.append(sub_img_segmentation_file_path)

    def validate_img_segmentation_pair(self, img_file_path, segmentation_file_path):
        if not img_file_path.exists():
            logging.warning(f"Missing image file: {img_file_path}")
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), str(img_file_path))
        if not segmentation_file_path.exists():
            logging.warning(f"Missing segmentation file: {segmentation_file_path}")
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), str(segmentation_file_path))
