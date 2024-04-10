import sys
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QTreeView,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QInputDialog,
    QMessageBox
)
from PyQt5.QtGui import QStandardItem, QStandardItemModel,  QColor
import numpy as np
import re


class TreeWindow(QMainWindow):
    class CustomTreeView(QTreeView):
        def __init__(self, tree_window):
            super().__init__()
            self.tree_window = tree_window

        def mouseDoubleClickEvent(self, event):
            index = self.indexAt(event.pos())
            item = self.model().itemFromIndex(index)
            if item and not item.hasChildren():
                new_text, ok = QInputDialog.getText(
                    self,
                    "Редактирование узла",
                    "Введите новое значение узла:",
                    text=item.text()
                )
                if ok:
                    if re.match("^-?\d+$", new_text):
                        item.setText(new_text)
                        self.tree_window.update_values(item)
                    else:
                        QMessageBox.warning(
                            self,
                            "Ошибка",
                            "Значением узла может быть только число."
                        )
            else:
                QMessageBox.warning(
                    self,
                    "Ошибка",
                    "Редактировать можно только листья дерева"
                )

    def update_values(self, item):
        if item:
            if item.hasChildren():
                child_values = np.array(
                    [
                        int(
                            item.child(i).text()
                        ) for i in range(item.rowCount())
                    ]
                )
                for i in range(item.rowCount()):
                    self.update_values(item.child(i))
                item_value = np.sum(child_values)
                item.setText(str(item_value))
                self.checking_sign_second_node(item_value.item(), item)
            parent = item.parent()
            while parent:
                child_values = np.array(
                    [
                        int(
                            parent.child(i).text()
                        ) for i in range(parent.rowCount())
                    ]
                )
                parent_value = np.sum(child_values)
                parent.setText(str(parent_value))
                self.checking_sign_second_node(parent_value.item(), parent)
                item = parent
                parent = item.parent()

    def checking_sign_second_node(self, value, node):
        if node.parent() and node.parent().parent() is None:
            if value > 0:
                node.setBackground(QColor("green"))
            elif value < 0:
                node.setBackground(QColor("red"))

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Дерево чисел и график")
        self.setGeometry(100, 100, 800, 600)

        self.layout = QVBoxLayout()

        self.tree_view = self.CustomTreeView(self)
        self.model = QStandardItemModel()
        self.tree_view.setModel(self.model)

        self.layout.addWidget(self.tree_view)

        self.button_add = QPushButton("Добавить узел")
        self.button_delete = QPushButton("Удалить узел")
        self.layout.addWidget(self.button_add)
        self.layout.addWidget(self.button_delete)

        self.central_widget = QWidget()
        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)

        self.button_add.clicked.connect(self.add_node)
        self.button_delete.clicked.connect(self.delete_node)

    def add_node(self):
        parent_index = self.tree_view.currentIndex()
        parent_item = self.model.itemFromIndex(
            parent_index
        ) if parent_index.isValid() else self.model.invisibleRootItem()
        new_node_name, ok = QInputDialog.getText(
            self,
            "Добавление узла",
            "Введите значение узла:"
        )
        if ok:
            if re.match("^-?\d+$", new_node_name):
                new_item = QStandardItem(new_node_name)
                parent_item.appendRow(new_item)
            else:
                QMessageBox.warning(
                    self,
                    "Ошибка",
                    "Значением узла может быть только число."
                )
        self.update_values(parent_item)

    def delete_node(self):
        selected_indexes = self.tree_view.selectedIndexes()
        for index in selected_indexes:
            item = self.model.itemFromIndex(index)
            if item and not item.hasChildren():
                parent = item.parent()
                if parent:
                    parent.removeRow(item.row())
                    self.update_values(parent)
                    if parent.rowCount() == 0:
                        parent.setText("0")
                        self.update_values(parent)
                else:
                    self.model.removeRow(item.row())
            else:
                QMessageBox.warning(
                    self,
                    "Ошибка",
                    "Удалить можно только листья дерева"
                )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TreeWindow()
    window.show()
    sys.exit(app.exec_())
