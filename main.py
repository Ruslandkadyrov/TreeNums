import random
import sys
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QTreeView,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QInputDialog,
    QMessageBox,
    QSplitter
)
from PyQt5.QtGui import QStandardItem, QStandardItemModel, QColor
from PyQt5.QtCore import pyqtSignal
import numpy as np
import pyqtgraph as pg
import re
import h5py


# Создаю окно наследуюясь от QMainWindow
class TreeWindow(QMainWindow):
    # Создаю наследника для переопределения двойного клика
    class CustomTreeView(QTreeView):
        # Сигнал для обновления графика
        nodeSignal = pyqtSignal()

        def __init__(self, tree_window):
            super().__init__()
            self.tree_window = tree_window

        # Метод обработки двойного щелчка мыши на элементе дерева.
        def mouseDoubleClickEvent(self, event):
            # Получаем индекс элемента дерева по позиции клика мыши в event.pos().
            index = self.indexAt(event.pos())
            # Получаем элемент дерева по индексу.
            item = self.model().itemFromIndex(index)
            # Проверяем, что элемент найден и у него нет дочерних элементов,
            # так как менять разрешено только листья
            if item and not item.hasChildren():
                # Открывам диалговео окно для ввода нового значения элемента.
                # ВВод нового значения в переменную new_text.
                # True, если пользователь нажмет "OK".
                new_text, ok = QInputDialog.getText(
                    self,
                    "Редактирование узла",
                    "Введите новое значение узла:",
                    text=item.text()
                )
                if ok:
                    # Проверяем, что новое значение соответствует регулярному вырожению
                    if re.match("^-?\d+$", new_text):
                        # Устанавливаем новый текст для элемента дерева.
                        item.setText(new_text)
                        # Устанавливаем цвет если уровень изменяемого узла второй
                        self.tree_window.checking_sign_second_node(
                            int(new_text), item
                        )
                        # Вызываем метол, чтобы обновить значение родителей
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

    def __init__(self):
        super().__init__()
        # Окно
        # Наименование окна
        self.setWindowTitle("Дерево чисел и график")
        # РАзмер окна и положение
        self.setGeometry(100, 100, 800, 600)
        # Определяем размещение элементов по вертикали
        self.layout = QVBoxLayout()

        # Разделяем окно на две части
        self.splitter = QSplitter(self)
        self.layout.addWidget(self.splitter)

        # Дерево
        # создаем объект CustomTreeView который от QTreeView
        self.tree_view = self.CustomTreeView(self)
        # Создание модели данных
        self.model = QStandardItemModel()
        # Установка моделей для нашего CustomTreeView
        self.tree_view.setModel(self.model)
        # Добавляем дерево в layout (в компановку)
        self.layout.addWidget(self.tree_view)
        # Создаем кнопки
        self.button_add = QPushButton("Добавить узел")
        self.button_delete = QPushButton("Удалить узел")
        self.button_create_tree = QPushButton("Создать дерево случайной глубины")
        self.button_fill_values = QPushButton("Заполнить пустые листья дерева случайными значениями")
        self.save_button = QPushButton('Сохранить дерево в HDF5')
        self.download_button = QPushButton('Загрузить дерево из HDF5')
        # Доавляем кнопки в окно
        self.layout.addWidget(self.button_add)
        self.layout.addWidget(self.button_delete)
        self.layout.addWidget(self.button_create_tree)
        self.layout.addWidget(self.button_fill_values)
        self.layout.addWidget(self.save_button)
        self.layout.addWidget(self.download_button)
        # Создание виджета QWidget для управления layout.
        self.central_widget = QWidget()
        # Установка layout для центрального виджета.
        self.central_widget.setLayout(self.layout)
        # Установка центрального виджета как главного виджета окна
        self.setCentralWidget(self.central_widget)
        # Подключаем кнопки к своим методат обработки
        self.button_add.clicked.connect(self.add_node)
        self.button_delete.clicked.connect(self.delete_node)
        self.button_create_tree.clicked.connect(self.create_random_tree)
        self.button_fill_values.clicked.connect(self.fill_random_values)
        self.save_button.clicked.connect(self.save_button_clicked)
        self.download_button.clicked.connect(self.download_button_clicked)
        # График
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setMinimumWidth(250)
        self.plot_widget.setMaximumWidth(500)

        self.splitter.addWidget(self.plot_widget)
        self.splitter.addWidget(self.tree_view)

        # Подключаем сигнал к обнавлению графика
        self.tree_view.nodeSignal.connect(self.update_plot)

    # Обработчик создания рандномного дерева
    def create_random_tree(self, depth=0, max_depth=5, min_depth=4):
        # Создание корневого элемента
        root_item = QStandardItem()
        # Добавляем корневой элемент в моель
        self.model.appendRow(root_item)
        # Запускаем метод создания дерева
        self.create_random_tree_recursive(root_item, depth, max_depth, min_depth)

    def create_random_tree_recursive(self, parent_item, depth, max_depth, min_depth):
        # Если тукущая глубина больше либо равно минимальной,
        # то рандомно назначается количесто дочерних узлоа от 1 до 4
        # иначе назначается 4
        if depth >= min_depth:
            num_children = random.randint(1, 4)
        else:
            num_children = 4
        # тут в каждой итерации создается дочерний узел у parent_item
        for _ in range(num_children):
            new_item = QStandardItem()
            parent_item.appendRow(new_item)
            # проверяем текущая глубина должна быть меньше максимальной
            # также устанвлена 50% вероятность дальнейшей рекурсии
            if depth < max_depth and random.random() < 0.50:
                # при запуске рекурсии увеличиваем глубину на 1
                self.create_random_tree_recursive(new_item, depth + 1, max_depth, min_depth)

    def fill_random_values(self):
        # находим коренвой елемент
        root_item = self.model.invisibleRootItem()
        # запускаем рекурсивную функцию заполнения значениями
        self.fill_random_values_recursive(root_item)

    def fill_random_values_recursive(self, parent_item):
        if isinstance(parent_item, QStandardItem):
            if parent_item.rowCount() == 0:
                current_value = parent_item.text()
                if not current_value:  # Проверяем, пустое ли значение
                    random_value = random.randint(-100, 100)
                    parent_item.setText(str(random_value))
                    self.checking_sign_second_node(random_value, parent_item)
            else:
                for row in range(parent_item.rowCount()):
                    child_item = parent_item.child(row)
                    self.fill_random_values_recursive(child_item)
                    self.update_values(child_item)

    def save_button_clicked(self):
        tree_data = self.get_tree_data()
        file_name = 'tree_data.h5'  # Имя файла для сохранения
        self.save_tree_to_hdf(tree_data, file_name)

    def download_button_clicked(self):
        file_name = 'tree_data.h5'
        tree_data = self.load_tree_from_hdf(file_name)
        if tree_data:
            self.update_tree_view(tree_data)
            self.tree_view.nodeSignal.emit()

    def load_tree_from_hdf(self, file_name):
        tree_data = {}
        with h5py.File(file_name, 'r') as hdf_file:
            self.load_tree_recursive(hdf_file, tree_data)
        return tree_data

    def load_tree_recursive(self, group, data):
        for key in group.keys():
            if isinstance(group[key], h5py.Group):
                data[key] = {}
                self.load_tree_recursive(group[key], data[key])
            elif isinstance(group[key], h5py.Dataset):
                data[key] = group[key][()]

    def update_tree_view(self, tree_data, parent_item=None):
        if parent_item is None:
            parent_item = self.model.invisibleRootItem()
        for key, value in tree_data.items():
            if isinstance(value, dict):
                new_item = QStandardItem(key)
                parent_item.appendRow(new_item)
                self.checking_sign_second_node(int(key), new_item)
                self.update_tree_view(value, new_item)
            else:
                new_item = QStandardItem(str(value))
                self.checking_sign_second_node(int(value), parent_item)

    def save_tree_to_hdf(self, tree_data, file_name):
        with h5py.File(file_name, 'w') as hdf_file:
            self.save_tree_recursive(hdf_file, tree_data)

    def save_tree_recursive(self, group, data):
        if isinstance(data, dict):
            for key, value in data.items():
                sub_group = group.create_group(key)
                self.save_tree_recursive(sub_group, value)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                self.save_tree_recursive(group.create_group(str(i)), item)
        else:
            group.create_dataset('data', data=data)

    def get_tree_data(self, parent_item=None):
        if parent_item is None:
            parent_item = self.model.invisibleRootItem()
        data = {}
        for i in range(parent_item.rowCount()):
            item = parent_item.child(i)
            if item.hasChildren():
                data[item.text()] = self.get_tree_data(item)
            else:
                data[item.text()] = int(item.text())
        return data

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
                # Устанавливаем цвет если уровень добавляемого узла второй
                self.checking_sign_second_node(int(new_node_name), new_item)
            else:
                QMessageBox.warning(
                    self,
                    "Ошибка",
                    "Значением узла может быть только число."
                )
        self.update_values(parent_item)
        self.tree_view.nodeSignal.emit()

    def delete_node(self):
        selected_indexes = self.tree_view.selectedIndexes()
        for index in selected_indexes:
            item = self.model.itemFromIndex(index)
            parent = item.parent()
            if parent:
                parent.removeRow(item.row())
                self.update_values(parent)
                if parent.rowCount() == 0:
                    parent.setText("0")
                    self.update_values(parent)
            else:
                self.model.removeRow(item.row())
        self.tree_view.nodeSignal.emit()

    def update_values(self, item):
        if item:
            if item.hasChildren():
                child_values = np.array([
                    int(item.child(i).text()) if item.child(i).text() else 0 for i in range(item.rowCount())
                ])
                for i in range(item.rowCount()):
                    self.update_values(item.child(i))
                item_value = np.sum(child_values)
                item.setText(str(item_value))
                self.checking_sign_second_node(item_value.item(), item)
            
            parent = item.parent()
            while parent:
                child_values = np.array([
                    int(parent.child(i).text()) if parent.child(i).text() else 0 for i in range(parent.rowCount())
                ])
                parent_value = np.sum(child_values)
                parent.setText(str(parent_value))
                self.checking_sign_second_node(parent_value.item(), parent)
                item = parent
                parent = item.parent()
            self.tree_view.nodeSignal.emit()

    def checking_sign_second_node(self, value, node):
        if node.parent():
            if node.parent().parent() and node.parent().parent().parent() is None:
                if value > 0:
                    node.setBackground(QColor("green"))
                elif value < 0:
                    node.setBackground(QColor("red"))

    def calculate_avg_values(self, tree_item, level_values, level):
        if level == len(level_values):
            level_values.append([])

        node_text = tree_item.text()
        if node_text:
            try:
                value = int(node_text)
                level_values[level].append(value)
            except ValueError:
                pass

        for i in range(tree_item.rowCount()):
            self.calculate_avg_values(tree_item.child(i), level_values, level + 1)

    def get_tree_avg_values(self, tree_view):
        level_values = []
        self.calculate_avg_values(tree_view.model().invisibleRootItem(), level_values, 0)

        avg_values = [sum(level) / len(level) if level else None for level in level_values]
        return avg_values

    def update_plot(self):
        avg_values = self.get_tree_avg_values(self.tree_view)
        filtered_avg_values = [value for value in avg_values if value is not None]
        levels = list(range(len(filtered_avg_values)))
        self.plot_widget.clear()
        self.plot_widget.plot(levels,  filtered_avg_values, pen=pg.mkPen('b'))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TreeWindow()
    window.show()
    sys.exit(app.exec_())
