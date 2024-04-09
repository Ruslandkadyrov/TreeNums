import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTreeView, QVBoxLayout, QWidget, QPushButton, QInputDialog, QMessageBox
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtCore import Qt
import re


class TreeWindow(QMainWindow):
    class CustomTreeView(QTreeView):
        def mouseDoubleClickEvent(self, event):
            index = self.indexAt(event.pos())
            item = self.model().itemFromIndex(index)
                
            if item and not item.hasChildren():
                new_text, ok = QInputDialog.getText(self, "Edit Node", "Enter new node name:", text=item.text())
                if ok:
                    if re.match("^-?\d+$", new_text):
                        item.setText(new_text)
                    else:
                        QMessageBox.warning(self, "Error", "Node name should only contain numbers.")
            else:
                QMessageBox.warning(self, "Error", "Editing is only allowed for leaf nodes.")

    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Tree and Graph Window")
        self.setGeometry(100, 100, 800, 600)
        
        self.layout = QVBoxLayout()
        
        self.tree_view = self.CustomTreeView()
        self.model = QStandardItemModel()
        self.tree_view.setModel(self.model)
        
        self.layout.addWidget(self.tree_view)
        
        self.button_add = QPushButton("Add Node")
        self.button_delete = QPushButton("Delete Node")
        self.layout.addWidget(self.button_add)
        self.layout.addWidget(self.button_delete)
        
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)

        self.button_add.clicked.connect(self.add_node)
        self.button_delete.clicked.connect(self.delete_node)
        
    def add_node(self):
        parent_index = self.tree_view.currentIndex()
        parent_item = self.model.itemFromIndex(parent_index) if parent_index.isValid() else self.model.invisibleRootItem()
        
        new_node_name, ok = QInputDialog.getText(self, "Input Dialog", "Enter node name:")
        if ok:
            if re.match("^-?\d+$", new_node_name):
                new_item = QStandardItem(new_node_name)
                parent_item.appendRow(new_item)
            else:
                QMessageBox.warning(self, "Error", "Node name should only contain numbers.")

    def delete_node(self):
        selected_indexes = self.tree_view.selectedIndexes()
        for index in selected_indexes:
            item = self.model.itemFromIndex(index)
            if item and not item.hasChildren():
                parent = item.parent()
                if parent:
                    parent.removeRow(item.row())
                else:
                    self.model.removeRow(item.row())
            else:
                QMessageBox.warning(self, "Error", "Deletion is only allowed for leaf nodes.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TreeWindow()
    window.show()
    sys.exit(app.exec_())
