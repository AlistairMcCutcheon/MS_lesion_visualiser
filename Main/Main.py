import logging
import os
from pathlib import Path
import vtk
import slicer
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin, getNode, getNodes
from packages.utils.context_managers import TempDir, SetParameters, BlockMethod
from packages.segmentation.segmentation import SegmentationDir, View
from packages.testing.test_segmentation_dir import SegmentationDirectoryTest
# import nibabel as nib
import numpy as np
#
# Main
#

class Main(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "Main"  # TODO: make this more human readable by adding spaces
        self.parent.categories = ["Segmentation"]  # category (folders where the module shows up in the module selector)
        self.parent.dependencies = []  # TODO: add here list of module names that this module requires
        self.parent.contributors = ["Alistair McCutcheon (Monash University)"]
        # TODO: update with short description of the module and a link to online module documentation
        self.parent.helpText = """
This is an example of scripted loadable module bundled in an extension.
See more information in <a href="https://github.com/organization/projectname#Main">module documentation</a>.
"""
        self.parent.acknowledgementText = "This file was developed by Alistair McCutcheon, Monash University."


#
# MainWidget
#

class MainWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
    """Uses ScriptedLoadableModuleWidget base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent=None):
        """
        Called when the user opens the module the first time and the widget is initialized.
        """
        ScriptedLoadableModuleWidget.__init__(self, parent)
        VTKObservationMixin.__init__(self)  # needed for parameter node observation
        self.logic = None
        self.parameter_node = None

    def setup(self):
        """
        Called when the user opens the module the first time and the widget is initialized.
        """
        ScriptedLoadableModuleWidget.setup(self)

        # Load widget from .ui file (created by Qt Designer).
        # Additional widgets can be instantiated manually and added to self.layout.
        uiWidget = slicer.util.loadUI(self.resourcePath('UI/Main.ui'))
        self.layout.addWidget(uiWidget)
        self.ui = slicer.util.childWidgetVariables(uiWidget)

        # Set scene in MRML widgets. Make sure that in Qt designer the top-level qMRMLWidget's
        # "mrmlSceneChanged(vtkMRMLScene*)" signal in is connected to each MRML widget's.
        # "setMRMLScene(vtkMRMLScene*)" slot.
        uiWidget.setMRMLScene(slicer.mrmlScene)

        self.logic = MainLogic()

        # Connections

        # These connections ensure that we update parameter node when scene is closed
        self.addObserver(slicer.mrmlScene, slicer.mrmlScene.StartCloseEvent, self.onSceneStartClose)
        self.addObserver(slicer.mrmlScene, slicer.mrmlScene.EndCloseEvent, self.onSceneEndClose)

        # These connections ensure that whenever user changes some settings on the GUI, that is saved in the MRML scene
        # (in the selected parameter node).
        self.ui.pthLoadSegmentationDirectory.connect('currentPathChanged(QString)', self.updateParameterNodeFromGUI)
        self.ui.btnLoadDirectory.connect("clicked(bool)", self.onBtnLoadDirectory)
        self.ui.prevButton.connect("clicked(bool)", self.onPrevButton)
        self.ui.nextButton.connect("clicked(bool)", self.onNextButton)
        self.ui.btnCompare.connect("clicked(bool)", self.onCompareButton)

        # Make sure parameter node is initialized (needed for module reload)
        self.initializeParameterNode()

    def cleanup(self):
        """
        Called when the application closes and the module widget is destroyed.
        """
        self.removeObservers()

    def enter(self):
        """
        Called each time the user opens this module.
        """
        pass
        # Make sure parameter node exists and observed
        self.initializeParameterNode()

    def exit(self):
        """
        Called each time the user opens a different module.
        """
        # Do not react to parameter node changes (GUI will be updated when the user enters into the module)
        self.removeObserver(self.parameter_node, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)

    def onSceneStartClose(self, caller, event):
        """
        Called just before the scene is closed.
        """
        # Parameter node will be reset, do not use it anymore
        self.setParameterNode(None)

    def onSceneEndClose(self, caller, event):
        """
        Called just after the scene is closed.
        """
        # If this module is shown while the scene is closed then recreate a new parameter node immediately
        if self.parent.isEntered:
            self.initializeParameterNode()

    def initializeParameterNode(self):
        """
        Ensure parameter node exists and observed.
        """
        # Parameter node stores all user choices in parameter values, node selections, etc.
        # so that when the scene is saved and reloaded, these settings are restored.
        self.setParameterNode(self.logic.getParameterNode())

        # Select default input nodes if nothing is selected yet to save a few clicks for the user
        if self.parameter_node.GetNodeReference("InputVolume"):
            return
        firstVolumeNode = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLScalarVolumeNode")
        if firstVolumeNode:
            self.parameter_node.SetNodeReferenceID("InputVolume", firstVolumeNode.GetID())

    def setParameterNode(self, inputParameterNode):
        """
        Set and observe parameter node.
        Observation is needed because when the parameter node is changed then the GUI must be updated immediately.
        """
        if inputParameterNode:
            self.logic.set_default_params(inputParameterNode)

        # Unobserve previously selected parameter node and add an observer to the newly selected.
        # Changes of parameter node are observed so that whenever parameters are changed by a script or any other module
        # those are reflected immediately in the GUI.
        if self.parameter_node is not None:
            self.removeObserver(self.parameter_node, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)
        self.parameter_node = inputParameterNode
        if self.parameter_node is not None:
            self.addObserver(self.parameter_node, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)

        # Initial GUI update
        self.updateGUIFromParameterNode()

    def updateGUIFromParameterNode(self, caller=None, event=None):
        """
        This method is called whenever parameter node is changed.
        The module GUI is updated to show the current state of the parameter node.
        """

        def compare_seg_dir_and_attempted_seg_dir():
            seg_dir_path = self.parameter_node.GetParameter("segmentation_dir_path")
            attempted_seg_dir_path = self.parameter_node.GetParameter("attempted_segmentation_dir_path")

            if seg_dir_path == attempted_seg_dir_path:
                return
            if not os.path.isdir(attempted_seg_dir_path):
                return
            with SetParameters(self.parameter_node) as parameter_node:
                parameter_node.SetParameter("segmentation_dir_path", attempted_seg_dir_path)
                parameter_node.SetParameter("segmentation_img_index", "0")

        def index_modified() -> bool:
            return not self.logic.segmentation.index == int(self.parameter_node.GetParameter("index"))

        def view_modified() -> bool:
            return not self.logic.segmentation.view.value == int(self.parameter_node.GetParameter("view"))

        def seg_dir_modified() -> bool:
            return not self.logic.segmentation.dir_path == self.parameter_node.GetParameter("segmentation_dir_path")

        def update_seg_dir():
            if not seg_dir_modified():
                return
            if self.logic.segmentation is not None:
                self.logic.segmentation.unload()
            self.logic.segmentation = SegmentationDir(self.parameter_node.GetParameter("segmentation_dir_path"))
        
        if self.parameter_node is None:
            return

        compare_seg_dir_and_attempted_seg_dir()
        load_dir = seg_dir_modified() or index_modified() or view_modified()
        update_seg_dir()
        
        if load_dir:
            self.logic.segmentation.load_index(
                View(int(self.parameter_node.GetParameter("view"))),
                int(self.parameter_node.GetParameter("index"))
            )

        # Make sure GUI changes do not call updateParameterNodeFromGUI (it could cause infinite loop)
        with BlockMethod(self, "updateParameterNodeFromGUI"):
            self.set_view_and_index(
                View(int(self.parameter_node.GetParameter("view"))),
                int(self.parameter_node.GetParameter("index"))
            )
            self.set_load_directory(self.parameter_node.GetParameter("attempted_segmentation_dir_path"))

    def updateParameterNodeFromGUI(self, caller=None, event=None):
        """
        This method is called when the user makes any change in the GUI.
        The changes are saved into the parameter node (so that they are restored when the scene is saved and loaded).
        """

        if self.parameter_node is None:
            return

        with SetParameters(self.parameter_node) as parameter_node:
            parameter_node.SetParameter("intermediate_attempted_segmentation_dir_path", self.ui.pthLoadSegmentationDirectory.currentPath)

    def set_load_directory(self, dir_path: str):
        if not os.path.isdir(dir_path):
            self.ui.lblValidDirectoryPathWarning.setText("Please enter a valid directory path")
            self.ui.lblValidDirectoryPathWarning.setStyleSheet('color: red')
            self.ui.btnLoadDirectory.setEnabled(False)
            return

        self.ui.lblValidDirectoryPathWarning.setText("Click 'Load Directory' to load the directory.")
        self.ui.lblValidDirectoryPathWarning.setStyleSheet('color: green')
        self.ui.btnLoadDirectory.setEnabled(True)


    def set_view_and_index(self, view: View, index: int) -> None:
        if view == View.STANDARD:
            self.ui.btnCompare.text = "Compare with Previous Image"
            self.ui.nextButton.setEnabled(self.logic.segmentation.index_is_valid_for_img(index + 1))
            self.ui.prevButton.setEnabled(self.logic.segmentation.index_is_valid_for_img(index - 1))
            self.ui.btnCompare.setEnabled(self.logic.segmentation.index_is_valid_for_sub_img(index - 1))
            return
        if view == View.SUB:
            self.ui.btnCompare.text = "Return to Standard View"
            self.ui.nextButton.setEnabled(False)
            self.ui.prevButton.setEnabled(False)
            self.ui.btnCompare.setEnabled(True)
            return

    def onBtnLoadDirectory(self):
        with SetParameters(self.parameter_node) as parameter_node:
            parameter_node.SetParameter("attempted_segmentation_dir_path", self.ui.pthLoadSegmentationDirectory.currentPath)

    def onPrevButton(self):
        self.parameter_node.SetParameter("index", self.logic.segmentation.index - 1)

    def onNextButton(self):
        self.parameter_node.SetParameter("index", self.logic.segmentation.index + 1)

    def onCompareButton(self):
        if self.logic.segmentation.view == View.STANDARD:
            self.parameter_node.SetParameter("view", str(View.SUB))
            return
        if self.logic.segmentation.view == View.SUB:
            self.parameter_node.SetParameter("view", str(View.STANDARD))
            return


#
# MainLogic
#

class MainLogic(ScriptedLoadableModuleLogic):
    """This class should implement all the actual
    computation done by your module.  The interface
    should be such that other python code can import
    this class and make use of the functionality without
    requiring an instance of the Widget.
    Uses ScriptedLoadableModuleLogic base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self):
        """
        Called when the logic class is instantiated. Can be used for initializing member variables.
        """
        ScriptedLoadableModuleLogic.__init__(self)
        self.segmentation = None

    def set_default_params(self, parameterNode):
        """
        Initialize parameter node with default settings.
        """
        if not parameterNode.GetParameter("segmentation_dir_path"):
            parameterNode.SetParameter("segmentation_dir_path", "")
        if not parameterNode.GetParameter("attempted_segmentation_dir_path"):
            parameterNode.SetParameter("attempted_segmentation_dir_path", "")
        if not parameterNode.GetParameter("intermediate_attempted_segmentation_dir_path"):
            parameterNode.SetParameter("intermediate_attempted_segmentation_dir_path", "")
        if not parameterNode.GetParameter("view"):
            parameterNode.SetParameter("view", "1")
        if not parameterNode.GetParameter("index"):
            parameterNode.SetParameter("index", "0")

    def load_index(self, view: View, index: int) -> None:
        self.segmentation.load_index(view, index)

    def load_dir(self, dir_path) -> None:
        if self.segmentation is not None:
            self.segmentation.unload()

        self.segmentation = SegmentationDir(dir_path)
        self.load_index(View.STANDARD, 0)

#
# MainTest
#

class MainTest(ScriptedLoadableModuleTest):
    """
    This is the test case for your scripted module.
    Uses ScriptedLoadableModuleTest base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def setUp(self):
        """ Do whatever is needed to reset the state - typically a scene clear will be enough.
        """
        slicer.mrmlScene.Clear()

    def runTest(self):
        """Run as few or as many tests as needed here.
        """
        self.delayDisplay("Starting the test")
        logging.disable(logging.CRITICAL)
        self.setUp()
        with TempDir(Path(__file__).parent.parent / "temp_test_assets") as temp_dir_path:
            SegmentationDirectoryTest(temp_dir_path).runTest()
        logging.disable(logging.NOTSET)
        self.delayDisplay('Test passed')
