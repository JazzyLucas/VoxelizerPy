import logging
import sys
from PyQt5 import QtWidgets, QtGui, QtCore
import pymesh
# this code sucks


class Voxelizer(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # Create a label for displaying instructions
        self.instructions = QtWidgets.QLabel("Drag and drop an .obj file here")
        self.instructions.setAlignment(QtCore.Qt.AlignCenter)

        # Create a button for performing the voxelization
        self.convert_button = QtWidgets.QPushButton("Convert")
        self.convert_button.clicked.connect(self.convert_obj)
        self.convert_button.setEnabled(False)

        # Create a layout for the widgets
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.instructions)
        layout.addWidget(self.convert_button)

        # Set the window properties
        self.setAcceptDrops(True)
        self.setWindowTitle("Voxelizer")

    def dragEnterEvent(self, event):
        print("DropEntered")
        if event.mimeData().hasFormat("text/uri-list"):
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        print("DropReceived")
        file_path = event.mimeData().urls()[0].toLocalFile()
        if file_path.endswith(".obj"):
            self.file_path = file_path
            self.instructions.setText("File ready for conversion")
            self.convert_button.setEnabled(True)
        else:
            self.instructions.setText("Invalid file format")
            self.convert_button.setEnabled(False)

    def convert_obj(self):
        print("Loading")
        # Load the original .obj file
        mesh = pymesh.load_mesh(self.file_path)

        # Voxelize the mesh
        print("Voxelizing")
        voxelized_mesh = pymesh.voxelize(mesh, 0.1)

        # Save the voxelized mesh as a new .obj file
        print("Saving")
        pymesh.save_mesh("voxelized.obj", voxelized_mesh)
        self.instructions.setText("File converted and saved as voxelized.obj")
        self.convert_button.setEnabled(False)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    voxelizer = Voxelizer()
    voxelizer.show()
    sys.exit(app.exec_())
