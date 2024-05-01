cmake_minimum_required(VERSION 3.16.3...3.19.7 FATAL_ERROR)

project(SlicerMSLesionVisualiser)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "https://github.com/AlistairMcCutcheon/SlicerMSLesionVisualiser#readme")
set(EXTENSION_CATEGORY "Segmentation")
set(EXTENSION_CONTRIBUTORS "Alistair McCutcheon (Monash University)")
set(EXTENSION_DESCRIPTION "Loads and displays multi-timepoint MS (multiple sclerosis) lesion images and segmentations.")
set(EXTENSION_ICONURL "https://raw.githubusercontent.com/AlistairMcCutcheon/SlicerMSLesionVisualiser/main/assets/icon.png")
set(EXTENSION_SCREENSHOTURLS "https://raw.githubusercontent.com/AlistairMcCutcheon/SlicerMSLesionVisualiser/main/assets/screenshot.png")
set(EXTENSION_DEPENDS "NA") # Specified as a list or "NA" if no dependencies

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(LoadMSLesionData)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
