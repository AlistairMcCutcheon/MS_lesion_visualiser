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

    def test_empty_dir(self):
        with TempDir(Path(self.test_dir_path) / "test_empty_dir") as temp_dir_path:
            try:
                SegmentationDir(dir_path=temp_dir_path)
            except InvalidSegmentationDirError:
                return
            raise TestFailedError()

    def test_combinations_of_files(self):
        @dataclass
        class FileCombination:
            num_imgs: int
            num_imgs_segmentations: int
            num_sub_imgs: int
            num_sub_imgs_segmentations: int
            def __str__(self):
                return f"{self.num_imgs}_{self.num_imgs_segmentations}_{self.num_sub_imgs}_{self.num_sub_imgs_segmentations}"

        def test_combination(combination: FileCombination):
            with TempDir(Path(self.test_dir_path) / str(combination)) as temp_dir_path:
                imgs_paths = [
                    Path(temp_dir_path) / 
                    file_type_to_name(FileType.IMG, i) for i in range(combination.num_imgs)
                ]
                imgs_segmentations_paths = [
                    Path(temp_dir_path) / 
                    file_type_to_name(FileType.IMG_SEGMENTATION, i) for i in range(combination.num_imgs_segmentations)
                ]
                sub_imgs_paths = [
                    Path(temp_dir_path) / 
                    file_type_to_name(FileType.SUB_IMG, i) for i in range(combination.num_sub_imgs)
                ]
                sub_imgs_segmentations_paths = [
                    Path(temp_dir_path) / 
                    file_type_to_name(FileType.SUB_IMG_SEGMENTATION, i) for i in range(combination.num_sub_imgs_segmentations)
                ]
                [open(img_path, "w").close() for img_path in imgs_paths]
                [open(img_segmentation_path, "w").close() for img_segmentation_path in imgs_segmentations_paths]
                [open(sub_img_path, "w").close() for sub_img_path in sub_imgs_paths]
                [open(sub_img_segmentation_path, "w").close() for sub_img_segmentation_path in sub_imgs_segmentations_paths]

                segmentation_dir = SegmentationDir(temp_dir_path)

            assert [str(x) for x in segmentation_dir.imgs_paths] == [str(x) for x in imgs_paths]
            assert [str(x) for x in segmentation_dir.imgs_segmentations_paths] == [str(x) for x in imgs_segmentations_paths]
            print([str(x) for x in segmentation_dir.sub_imgs_paths])
            print([str(x) for x in sub_imgs_paths])
            assert [str(x) for x in segmentation_dir.sub_imgs_paths] == [str(x) for x in sub_imgs_paths]
            assert [str(x) for x in segmentation_dir.sub_imgs_segmentations_paths] == [str(x) for x in sub_imgs_segmentations_paths]


        file_combinations = [
            FileCombination(1, 1, 0, 0),
            FileCombination(2, 2, 0, 0),
        ]
        [test_combination(file_combination) for file_combination in file_combinations]
        pass

    # def test_1_img_1_segmentation(self):
    #     with TempDir(Path(self.test_dir_path) / "test_1_img_1_segmentation") as temp_dir_path:
    #         img_0_path = Path(temp_dir_path) / file_type_to_name(FileType.IMG, 0)
    #         img_0_segmentation_path = Path(temp_dir_path) / file_type_to_name(FileType.IMG_SEGMENTATION, 0)
    #         open(img_0_path, "w").close()
    #         open(img_0_segmentation_path, "w").close()
    #         segmentation_dir = SegmentationDir(temp_dir_path)
    #     print([str(x) for x in segmentation_dir.imgs_paths])
    #     print([str(img_0_path)])
    #     assert [str(x) for x in segmentation_dir.imgs_paths] == [str(img_0_path)]
    #     assert [str(x) for x in segmentation_dir.imgs_segmentations_paths] == [str(img_0_segmentation_path)]
    #     assert segmentation_dir.sub_imgs_paths == []
    #     assert segmentation_dir.sub_imgs_segmentations_paths == []

    # def test_2_img_2_segmentation(self):
    #     with TempDir(Path(self.test_dir_path) / "test_2_img_2_segmentation") as temp_dir_path:
    #         img_0_path = Path(temp_dir_path) / file_type_to_name(FileType.IMG, 0)
    #         img_0_segmentation_path = Path(temp_dir_path) / file_type_to_name(FileType.IMG_SEGMENTATION, 0)
    #         img_1_path = Path(temp_dir_path) / file_type_to_name(FileType.IMG, 1)
    #         img_1_segmentation_path = Path(temp_dir_path) / file_type_to_name(FileType.IMG_SEGMENTATION, 1)
    #         open(img_0_path, "w").close()
    #         open(img_1_path, "w").close()
    #         open(img_0_segmentation_path, "w").close()
    #         open(img_1_segmentation_path, "w").close()
    #         segmentation_dir = SegmentationDir(temp_dir_path)
    #     assert [str(x) for x in segmentation_dir.imgs_paths] == [str(img_0_path), str(img_1_path)]
    #     assert [str(x) for x in segmentation_dir.imgs_segmentations_paths] == [str(img_0_segmentation_path), str(img_1_segmentation_path)]
    #     assert segmentation_dir.sub_imgs_paths == []
    #     assert segmentation_dir.sub_imgs_segmentations_paths == []

    # def test_1_img_0_segmentation(self):
    #     with TempDir(Path(self.test_dir_path) / "test_1_img_0_segmentation") as temp_dir_path:
    #         open(Path(temp_dir_path) / file_type_to_name(FileType.IMG, 0), "w").close()
    #         try:
    #             SegmentationDir(temp_dir_path)
    #         except InvalidSegmentationDirError:
    #             return
    #     raise TestFailedError

    # def test_0_img_1_segmentation(self):
    #     with TempDir(Path(self.test_dir_path) / "test_0_img_1_segmentation") as temp_dir_path:
    #         open(Path(temp_dir_path) / file_type_to_name(FileType.IMG_SEGMENTATION, 0), "w").close()
    #         try:
    #             SegmentationDir(temp_dir_path)
    #         except InvalidSegmentationDirError:
    #             return
    #     raise TestFailedError

    # def test_1_img_2_segmentation(self):
    #     with TempDir(Path(self.test_dir_path) / "test_1_img_2_segmentation") as temp_dir_path:
    #         open(Path(temp_dir_path) / file_type_to_name(FileType.IMG, 0), "w").close()
    #         open(Path(temp_dir_path) / file_type_to_name(FileType.IMG_SEGMENTATION, 0), "w").close()
    #         open(Path(temp_dir_path) / file_type_to_name(FileType.IMG_SEGMENTATION, 1), "w").close()
    #         try:
    #             SegmentationDir(temp_dir_path)
    #         except InvalidSegmentationDirError:
    #             return
    #     raise TestFailedError

    # def test_2_img_1_segmentation(self):
    #     with TempDir(Path(self.test_dir_path) / "test_1_img_2_segmentation") as temp_dir_path:
    #         open(Path(temp_dir_path) / file_type_to_name(FileType.IMG, 0), "w").close()
    #         open(Path(temp_dir_path) / file_type_to_name(FileType.IMG, 1), "w").close()
    #         open(Path(temp_dir_path) / file_type_to_name(FileType.IMG_SEGMENTATION, 0), "w").close()
    #         try:
    #             SegmentationDir(temp_dir_path)
    #         except InvalidSegmentationDirError:
    #             return
    #     raise TestFailedError

    # def test_1_sub_img_1_sub_segmentation(self):
    #     with TempDir(Path(self.test_dir_path) / "test_0_img_1_segmentation") as temp_dir_path:
    #         open(Path(temp_dir_path) / SegmentationDirFileNames.img_segmentation(0), "w").close()
    #         try:
    #             SegmentationDir(temp_dir_path)
    #         except InvalidSegmentationDirError:
    #             return
    #     raise TestFailedError
