cmake_minimum_required(VERSION 3.16.3...3.19.7 FATAL_ERROR)

project(MS_lesion_visualiser)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "https://www.slicer.org/wiki/Documentation/Nightly/Extensions/MS_lesion_visualiser")
set(EXTENSION_CATEGORY "Segmentation")
set(EXTENSION_CONTRIBUTORS "Alistair McCutcheon (Monash University)")
set(EXTENSION_DESCRIPTION "A tool to visualise multiple sclerosis lesion MRI images and segmentations.")
set(EXTENSION_ICONURL "https://www.example.com/Slicer/Extensions/MS_lesion_visualiser.png")
set(EXTENSION_SCREENSHOTURLS "https://www.example.com/Slicer/Extensions/MS_lesion_visualiser/Screenshots/1.png")
set(EXTENSION_DEPENDS "NA") # Specified as a list or "NA" if no dependencies

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(LoadMSLesiondirectory)
add_subdirectory(test_module)
add_subdirectory(Main)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
