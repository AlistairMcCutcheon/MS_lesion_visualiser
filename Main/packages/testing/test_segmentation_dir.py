import inspect
from packages.segmentation.segmentation import SegmentationDir, InvalidSegmentationDirError
from packages.segmentation.file_types import FileType, file_type_to_name
from pathlib import Path
from packages.testing.utils import *
from packages.utils.temp_dir import TempDir
import logging
from dataclasses import dataclass

class SegmentationDirectoryTest:
    def __init__(self, test_dir_path: str) -> None:
        self.test_dir_path = test_dir_path

    def runTest(self):
        """Run as few or as many tests as needed here.
        """
        for method_name, method in inspect.getmembers(self, predicate=inspect.ismethod):
            if not method_name.startswith("test_"):
                continue
            method()
            logging.debug(f"Completed: {method_name}")

    def test_invalid_path(self):
        try:
            SegmentationDir(dir_path="/not/a/valid/path")
        except InvalidSegmentationDirError:
            return
        raise TestFailedError()

    def test_missing_dir(self):
        try:
            SegmentationDir(Path(self.test_dir_path) / "test_missing_dir")
        except InvalidSegmentationDirError:
            return
        raise TestFailedError()

    def test_combinations_of_files(self):
        @dataclass
        class FileCombination:
            img_indices: tuple[int]
            imgs_segmentations_indices: tuple[int]
            sub_imgs_indices: tuple[int]
            sub_imgs_segmentations_indices: tuple[int]
            def __hash__(self) -> int:
                return hash((self.img_indices, self.imgs_segmentations_indices, self.sub_imgs_indices, self.sub_imgs_segmentations_indices))

        def test_combination(combination: FileCombination, exception : Exception = None) -> None:
            with TempDir(Path(self.test_dir_path) / str(hash(combination))) as temp_dir_path:
                imgs_paths = {
                    i: Path(temp_dir_path) / 
                    file_type_to_name(FileType.IMG, i) 
                    for i in combination.img_indices
                }
                imgs_segmentations_paths = {
                    i: Path(temp_dir_path) / 
                    file_type_to_name(FileType.IMG_SEGMENTATION, i) 
                    for i in combination.imgs_segmentations_indices
                }
                sub_imgs_paths = {
                    i: Path(temp_dir_path) / 
                    file_type_to_name(FileType.SUB_IMG, i) 
                    for i in combination.sub_imgs_indices
                }
                sub_imgs_segmentations_paths = {
                    i: Path(temp_dir_path) / 
                    file_type_to_name(FileType.SUB_IMG_SEGMENTATION, i) 
                    for i in combination.sub_imgs_segmentations_indices
                }
                [open(img_path, "w").close() for img_path in imgs_paths.values()]
                [open(img_segmentation_path, "w").close() for img_segmentation_path in imgs_segmentations_paths.values()]
                [open(sub_img_path, "w").close() for sub_img_path in sub_imgs_paths.values()]
                [open(sub_img_segmentation_path, "w").close() for sub_img_segmentation_path in sub_imgs_segmentations_paths.values()]

                if exception is None:
                    segmentation_dir = SegmentationDir(temp_dir_path)
                else:
                    try:
                        SegmentationDir(temp_dir_path)
                    except exception:
                        return
                    raise TestFailedError

            assert {x: str(y) for x, y in segmentation_dir.imgs_paths.items()} == {x: str(y) for x, y in imgs_paths.items()}
            assert {x: str(y) for x, y in segmentation_dir.imgs_segmentations_paths.items()} == {x: str(y) for x, y in imgs_segmentations_paths.items()}
            assert {x: str(y) for x, y in segmentation_dir.sub_imgs_paths.items()} == {x: str(y) for x, y in sub_imgs_paths.items()}
            assert {x: str(y) for x, y in segmentation_dir.sub_imgs_segmentations_paths.items()} == {x: str(y) for x, y in sub_imgs_segmentations_paths.items()}


        test_file_combination_outcome = {
            FileCombination((), (), (), ()): InvalidSegmentationDirError,
            FileCombination((0,), (0,), (), ()): None,
            FileCombination((0, 1), (0, 1), (), ()): None,
            FileCombination((0,), (), (), ()): InvalidSegmentationDirError,
            FileCombination((), (0,), (), ()): InvalidSegmentationDirError,
            FileCombination((0,), (0, 1), (), ()): InvalidSegmentationDirError,
            FileCombination((0, 1), (0,), (), ()): InvalidSegmentationDirError,
            FileCombination((0, 1, 2), (0, 1, 2), (), ()): None,
            FileCombination((), (), (0,), (0,)): InvalidSegmentationDirError,
        }

        for file_combination, exception in test_file_combination_outcome.items():
            if exception is None:
                test_combination(file_combination)
                continue
            try:
                test_combination(file_combination)
            except exception:
                continue
            raise TestFailedError(f"{file_combination} did not raise {exception}")
