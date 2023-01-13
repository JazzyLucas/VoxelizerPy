import sys
from PyQt5.QtCore import Qt, QFileInfo
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QFileDialog
import numpy as np
from matplotlib import tri
import json


class Voxelizer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setWindowTitle("Voxelizer")
        self.setGeometry(100, 100, 600, 400)
        self.label = QLabel("Drag and drop a model file to voxelize", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setGeometry(0, 0, 600, 400)
        self.show()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        file_path = event.mimeData().urls()[0].toLocalFile()
        file_info = QFileInfo(file_path)
        if file_info.suffix() in ["obj"]:
            self.voxelize_model(file_path)
        else:
            self.label.setText("Invalid file format")

    def voxelize_model(self, file_path):
        # Load the obj file
        with open(file_path) as f:
            lines = f.readlines()
            vertices = []
            faces = []
            for line in lines:
                if line.startswith("v "):
                    vertices.append(list(map(float, line.strip().split()[1:])))
                elif line.startswith("f "):
                    faces.append(list(map(int, line.strip().split()[1:])))

        # Define the resolution of the voxel grid
        resolution = 0.1

        # Create the voxel grid
        x_min, y_min, z_min = np.min(vertices, axis=0)
        x_max, y_max, z_max = np.max(vertices, axis=0)
        x_grid, y_grid, z_grid = np.mgrid[
                                 x_min:x_max:resolution,
                                 y_min:y_max:resolution,
                                 z_min:z_max:resolution
                                 ]
        voxel_grid = np.zeros(x_grid.shape, dtype=bool)

        # Iterate over the triangles of the 3D model
        triangulation = tri.Triangulation(
            [vertex[0] for vertex in vertices],
            [vertex[1] for vertex in vertices],
            faces
        )
        for simplex in triangulation.simplices:
            # Extract the coordinates of the vertices of the current triangle
            x = [vertices[i - 1][0] for i in simplex]
            y = [vertices[i - 1][1] for i in simplex]
            z = [vertices[i - 1][2] for i in simplex]
            # Find the voxels that are inside or intersecting with the triangle
            voxel_indices = np.where(
                np.logical_and.reduce([
                    x_grid >= min(x), x_grid < max(x),
                    y_grid >= min(y), y_grid < max(y),
                    z_grid >= min(z), z_grid < max(z)
                ])
            )
            # Set the voxels to be 'on'
            voxel_grid[voxel_indices] = True

        # save the voxelized model as json
        with open('voxelized_model.json', 'w') as fp:
            json.dump(voxel_grid.tolist(), fp)
        self.label.setText("Model voxelized successfully")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    voxelizer = Voxelizer()
    sys.exit(app.exec_())
