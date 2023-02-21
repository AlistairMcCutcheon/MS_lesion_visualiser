from enum import Enum, auto

class FileType(Enum):
    IMG = auto()
    IMG_SEGMENTATION = auto()
    SUB_IMG = auto()
    SUB_IMG_SEGMENTATION = auto()

def file_type_to_name(file_type: FileType, index: int) -> str:
    if file_type == FileType.IMG:
        return f"img_{index}.nii.gz"
    if file_type == FileType.IMG_SEGMENTATION:
        return f"img_{index}_segmentation.nrrd"
    if file_type == FileType.SUB_IMG:
        return f"img_sub_{index}.nii.gz"
    if file_type == FileType.SUB_IMG_SEGMENTATION:
        return f"img_sub_{index}_segmentation.nrrd"
    raise NotImplementedError(f"Unsupported enum value: {file_type}")



