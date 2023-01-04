import inspect
from packages.segmentation.segmentation import *
from packages.testing.utils import *
from packages.utils.temp_dir import TempDir
import logging

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

    def test_1_img_1_segmentation(self):
        with TempDir(Path(self.test_dir_path) / "test_1_img_1_segmentation") as temp_dir_path:
            open(Path(temp_dir_path) / SegmentationDirFileNames.img(0), "w").close()
            open(Path(temp_dir_path) / SegmentationDirFileNames.img_segmentation(0), "w").close()
            SegmentationDir(temp_dir_path)

    def test_2_img_2_segmentation(self):
        with TempDir(Path(self.test_dir_path) / "test_2_img_2_segmentation") as temp_dir_path:
            open(Path(temp_dir_path) / SegmentationDirFileNames.img(0), "w").close()
            open(Path(temp_dir_path) / SegmentationDirFileNames.img(1), "w").close()
            open(Path(temp_dir_path) / SegmentationDirFileNames.img_segmentation(0), "w").close()
            open(Path(temp_dir_path) / SegmentationDirFileNames.img_segmentation(1), "w").close()
            SegmentationDir(temp_dir_path)

    def test_1_img_0_segmentation(self):
        with TempDir(Path(self.test_dir_path) / "test_1_img_0_segmentation") as temp_dir_path:
            open(Path(temp_dir_path) / SegmentationDirFileNames.img(0), "w").close()
            try:
                SegmentationDir(temp_dir_path)
            except InvalidSegmentationDirError:
                return
        raise TestFailedError

    def test_0_img_1_segmentation(self):
        with TempDir(Path(self.test_dir_path) / "test_0_img_1_segmentation") as temp_dir_path:
            open(Path(temp_dir_path) / SegmentationDirFileNames.img_segmentation(0), "w").close()
            try:
                SegmentationDir(temp_dir_path)
            except InvalidSegmentationDirError:
                return
        raise TestFailedError

    def test_1_img_2_segmentation(self):
        with TempDir(Path(self.test_dir_path) / "test_1_img_2_segmentation") as temp_dir_path:
            open(Path(temp_dir_path) / SegmentationDirFileNames.img(0), "w").close()
            open(Path(temp_dir_path) / SegmentationDirFileNames.img_segmentation(0), "w").close()
            open(Path(temp_dir_path) / SegmentationDirFileNames.img_segmentation(1), "w").close()
            try:
                SegmentationDir(temp_dir_path)
            except InvalidSegmentationDirError:
                return
        raise TestFailedError

    def test_2_img_1_segmentation(self):
        with TempDir(Path(self.test_dir_path) / "test_1_img_2_segmentation") as temp_dir_path:
            open(Path(temp_dir_path) / SegmentationDirFileNames.img(0), "w").close()
            open(Path(temp_dir_path) / SegmentationDirFileNames.img(1), "w").close()
            open(Path(temp_dir_path) / SegmentationDirFileNames.img_segmentation(0), "w").close()
            try:
                SegmentationDir(temp_dir_path)
            except InvalidSegmentationDirError:
                return
        raise TestFailedError

    # def test_1_sub_img_1_sub_segmentation(self):
    #     with TempDir(Path(self.test_dir_path) / "test_0_img_1_segmentation") as temp_dir_path:
    #         open(Path(temp_dir_path) / SegmentationDirFileNames.img_segmentation(0), "w").close()
    #         try:
    #             SegmentationDir(temp_dir_path)
    #         except InvalidSegmentationDirError:
    #             return
    #     raise TestFailedError
