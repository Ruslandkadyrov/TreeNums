import os
import random
import re
import sys

import h5py
import numpy as np
import pyqtgraph as pg
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import (QApplication, QInputDialog, QMainWindow,
                             QMessageBox, QPushButton, QSplitter, QTreeView,
                             QVBoxLayout, QWidget)


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
            # Получаем индекс элемента дерева
            # по позиции клика мыши в event.pos()
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
                    # Проверяем, что новое значение соответствует
                    # регулярному вырожению
                    if re.match(r"^-?\d+$", new_text):
                        # Устанавливаем новый текст для элемента дерева.
                        item.setText(new_text)
                        # Устанавливаем цвет
                        # если уровень изменяемого узла второй
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
        self.splitter = QSplitter(Qt.Vertical, self)
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
        self.button_create_tree = QPushButton(
            "Создать дерево случайной глубины"
        )
        self.button_fill_values = QPushButton(
            "Заполнить пустые листья дерева случайными значениями"
        )
        self.save_button = QPushButton("Сохранить дерево в HDF5")
        self.download_button = QPushButton("Загрузить дерево из HDF5")
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

        # определяем расположение виджетов
        self.splitter.addWidget(self.tree_view)
        self.splitter.addWidget(self.plot_widget)
        # разделитель делим ровно по палам для дерева и графика
        self.splitter.setStretchFactor(1, 1)

        # Подключаем сигнал к обнавлению графика
        self.tree_view.nodeSignal.connect(self.update_plot)

    # Обработчик создания рандномного дерева
    def create_random_tree(self, depth=0, max_depth=5, min_depth=4):
        # Создание корневого элемента
        root_item = QStandardItem()
        # Добавляем корневой элемент в моель
        self.model.appendRow(root_item)
        # Запускаем метод создания дерева
        self.create_random_tree_recursive(
            root_item, depth, max_depth, min_depth
        )

    def create_random_tree_recursive(
            self, parent_item, depth, max_depth, min_depth
    ):
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
                self.create_random_tree_recursive(
                    new_item, depth + 1, max_depth, min_depth
                )

    def fill_random_values(self):
        # находим коренвой елемент
        root_item = self.model.invisibleRootItem()
        # запускаем рекурсивную функцию заполнения значениями
        self.fill_random_values_recursive(root_item)

    def fill_random_values_recursive(self, parent_item):
        # проверяем является ли parent_item экземпляром QStandardItem
        if isinstance(parent_item, QStandardItem):
            # проверяем есть ли дочерние элементы данного элеманта
            if parent_item.rowCount() == 0:
                # вытаскиваем занчение этого элемента
                current_value = parent_item.text()
                if not current_value:  # Проверяем, пустое ли значение
                    # рандомно выбирает число
                    random_value = random.randint(-100, 100)
                    # присваиваем это значение к нашему элементу
                    parent_item.setText(str(random_value))
                    # и прогоняем этот элемент через метод который назначает
                    # цвет если элемент является второго уровня
                    self.checking_sign_second_node(random_value, parent_item)
            else:
                # если же у входящего элемента есть дочерние элементы
                # итерируемся по дочерним элементам и рекурсией
                # присваеиваем им значения
                for row in range(parent_item.rowCount()):
                    child_item = parent_item.child(row)
                    self.fill_random_values_recursive(child_item)
                    # пересчитыввем значения элементов методом update_values
                    self.update_values(child_item)

    # Обработчик кнопки для сохраненения дерева в hdf
    def save_button_clicked(self):
        # Собираем данные дерева в tree_data с помощтью метода get_tree_data()
        tree_data = self.get_tree_data()
        # Имя файла для сохранения
        file_name = 'tree_data.h5'
        # Запускаем метод сохранения дерева в файл tree_data.h5
        self.save_tree_to_hdf(tree_data, file_name)

    def get_tree_data(self, parent_item=None):
        # если елемент не передан то назначением корнем модели
        if parent_item is None:
            parent_item = self.model.invisibleRootItem()
        data = {}
        # итерируемся по количеству дочерних элементов
        for i in range(parent_item.rowCount()):
            item = parent_item.child(i)
            # если в свою очередь i-ый элемент имеет дочерние элементы
            if item.hasChildren():
                # то в словарь добавляем ключ-текст элеменьа
                # а значением рекурсивно вызоваем метод
                data[item.text()] = self.get_tree_data(item)
            else:
                # пока не дойдем до элемента который не имеет дочернего элемнта
                # и записываем в словарь значение
                data[item.text()] = int(item.text())
        # итого получаем дерево в виде словаря
        return data

    # метод сохранения дерева в файл
    def save_tree_to_hdf(self, tree_data, file_name):
        # Получаем путь к директории
        current_dir = os.path.dirname(sys.argv[0])
        file_path = os.path.join(current_dir, file_name)
        with h5py.File(file_path, 'w') as hdf_file:
            # вызываем рекусривный метод для сохраненения данные дерева в файл
            self.save_tree_recursive(hdf_file, tree_data)

    # рекурсивный метод сохранения дерева в файл
    def save_tree_recursive(self, group, data):
        # если объект является словарем
        if isinstance(data, dict):
            # то для каждой пары ключ-згачение
            for key, value in data.items():
                # создается подгруппа с именем key
                sub_group = group.create_group(key)
                # рекусривно создаем подгруппы
                self.save_tree_recursive(sub_group, value)

    # метод обработки кнопки загрузки дерева из файла hdf
    def download_button_clicked(self):
        # устанавливаем имя файла
        file_name = 'tree_data.h5'
        # с помощью метода load_tree_from_hdf
        # выгружаем данные дерева в tree_data из файла
        tree_data = self.load_tree_from_hdf(file_name)
        # если данные дерева получены
        if tree_data:
            # то с помощью метода update_tree_view
            # изменяем представление данных дерева
            self.update_tree_view(tree_data)
            # подоем сигнал для обновления графика
            self.tree_view.nodeSignal.emit()

    # метод выгрузки дерева из файла
    def load_tree_from_hdf(self, file_name):
        tree_data = {}
        # открываем файл в режиме чтения
        with h5py.File(file_name, 'r') as hdf_file:
            # запускаем рекурсивный метод для сохрагнения дерева в tree_data
            self.load_tree_recursive(hdf_file, tree_data)
        return tree_data

    # метод сохранения дерева из файла, рекурсия
    def load_tree_recursive(self, group, data):
        # итерируемся по ключам объекта группы
        for key in group.keys():
            # если элемент по ключу является группой
            if isinstance(group[key], h5py.Group):
                # создаем пустой словарь в словаре data с ключем key
                data[key] = {}
                # вызываем рекусивно функцию
                self.load_tree_recursive(group[key], data[key])
            # если элемент является датасетом
            elif isinstance(group[key], h5py.Dataset):
                # данные копирубтся в словарь data
                data[key] = group[key][()]

    # метод изменения представления дерева
    def update_tree_view(self, tree_data, parent_item=None):
        # если узел не передан
        if parent_item is None:
            # то используем корневой элемент модели
            parent_item = self.model.invisibleRootItem()
        # итерируемся по паре ключ-значение слвоаря tree_data
        for key, value in tree_data.items():
            # если значение является словарем значит имеем вложенные данные
            if isinstance(value, dict):
                # создаем новый элемент со значение ключа
                new_item = QStandardItem(key)
                # доьавляем его в родительский элемент parent_item
                parent_item.appendRow(new_item)
                # проверяем нужно ли определить знак элемента и добавить цвет
                self.checking_sign_second_node(int(key), new_item)
                # рекуснивно вызываем метод update_tree_view
                # с новыми данными value и new_item
                self.update_tree_view(value, new_item)
            else:
                # если же нет вложенности
                # то создаем элемент со значением value
                new_item = QStandardItem(str(value))
                # проверяем нужно ли определить знак элемента и добавить цвет
                self.checking_sign_second_node(int(value), parent_item)

    # обработчик кнопки добавления узла
    def add_node(self):
        # получаем индекс выбранного элемента
        parent_index = self.tree_view.currentIndex()
        # если индекс действителен то получаем соотвествующий элемент модели
        # в противном слкчае берем корневой элемент модели
        parent_item = self.model.itemFromIndex(
            parent_index
        ) if parent_index.isValid() else self.model.invisibleRootItem()
        # Выходит диалоговое окно где предлагаетя ввести значение нового узла
        new_node_name, ok = QInputDialog.getText(
            self,
            "Добавление узла",
            "Введите значение узла:"
        )
        # если пользователь нажал ОК
        if ok:
            # если введенное значение число
            if re.match(r"^-?\d+$", new_node_name):
                # создаем новый элемент
                new_item = QStandardItem(new_node_name)
                # добвалем его как дочерний к выбранному узлу
                parent_item.appendRow(new_item)
                # Устанавливаем цвет если уровень добавляемого узла второй
                self.checking_sign_second_node(int(new_node_name), new_item)
            else:
                # если же значение не число то выводим ошибку
                QMessageBox.warning(
                    self,
                    "Ошибка",
                    "Значением узла может быть только число."
                )
        # запускаем метод для пересчета значении родительских узлов
        self.update_values(parent_item)
        # сигнализируем об обновлении графика
        self.tree_view.nodeSignal.emit()

    # обработчик кнопки удаления узла
    def delete_node(self):
        # получаем индекс выбранного элемента
        index = self.tree_view.currentIndex()
        # получаем элемент модели по этому индексу
        item = self.model.itemFromIndex(index)
        # обязательно должен быть выбран узел
        if item:
            # получаем родителя этого элемнта
            parent = item.parent()
            # если есть родитель
            if parent:
                # то удаляем выбранный узел
                parent.removeRow(item.row())
                # и обновляем значения родительских узлов
                self.update_values(parent)
                # если в этом родителськом узле не останется дочерних узлов
                if parent.rowCount() == 0:
                    # то присваиваем значение 0
                    parent.setText("0")
                    # и так же обновляем значения родительских узлов
                    self.update_values(parent)
            else:
                # если же нет родителя то просто удаляем узел из корня модели
                self.model.removeRow(item.row())
            # сигнализируем об обновлении графика
            self.tree_view.nodeSignal.emit()
        else:
            QMessageBox.warning(
                    self,
                    "Ошибка",
                    "Выберите узел"
                )

    # метод обнвления родительских узлов при добвалении/измении листьев дерева
    # или удалении узла
    def update_values(self, item):
        # проверяем было ли передан элемент
        if item:
            # если есть у этого элемента дочерний элемент
            if item.hasChildren():
                # Создаем массив NumPy значений дочерних элементов,
                # преобразуя текст в целое число или 0, если текст пустой.
                child_values = np.array([
                    int(item.child(i).text())
                    if item.child(i).text()
                    else 0 for i in range(item.rowCount())
                ])
                # Рекурсивно обновляем значения для каждого дочернего элемента.
                for i in range(item.rowCount()):
                    self.update_values(item.child(i))
                # Суммируем значения дочерних элементов.
                item_value = np.sum(child_values)
                # Устанваливаем это значение в текущий элемент
                item.setText(str(item_value))
                # проверяем нужно ли определить знак элемента и добавить цвет
                self.checking_sign_second_node(item_value.item(), item)
            # далее идет обнволение значении родителей этекущего элемнта
            parent = item.parent()   # определяем родителя
            # пока есть родитель
            while parent:
                # Создаем массив NumPy значений дочерних элементов,
                # преобразуя текст в целое число или 0, если текст пустой.
                child_values = np.array([
                    int(parent.child(i).text())
                    if parent.child(i).text()
                    else 0 for i in range(parent.rowCount())
                ])
                # Суммируем значения дочерних элементов этого родителя
                parent_value = np.sum(child_values)
                # устанавливаем новое значение этого родителя
                parent.setText(str(parent_value))
                # проверяем нужно ли определить знак элемента и добавить цвет
                self.checking_sign_second_node(parent_value.item(), parent)
                # получаем нового родителя для новой итерации
                item = parent
                parent = item.parent()
            # сигнализируем об обновлении графика
            self.tree_view.nodeSignal.emit()

    # метод устанановки цвета для второго уровня узла
    def checking_sign_second_node(self, value, node):
        # если есть у переданного узла родитель
        if node.parent():
            # проверяем является ли этот узел второго уронвя
            if (
                node.parent().parent()
                and node.parent().parent().parent() is None
            ):
                # если переданный узел является второго уровня
                # то в зависимости каким является его значениее определяем цвет
                if value > 0:
                    node.setBackground(QColor("green"))
                elif value < 0:
                    node.setBackground(QColor("red"))

    # обработчик сигнала об обновлении графика
    def update_plot(self):
        # с помощью метода get_tree_avg_values
        # возвращаем средние значения уровней из дерева self.tree_view
        avg_values = self.get_tree_avg_values(self.tree_view)
        # фильтруем от ненулевых значении
        filtered_avg_values = [
            value for value in avg_values if value is not None
        ]
        # определяем уровни дерева
        levels = list(range(len(filtered_avg_values)))
        # удаляем старый график перед обновлением
        self.plot_widget.clear()
        # строим график levels это ось Х и filtered_avg_values как ось Y
        # цвет линии синий и строим линии от точки до точки
        self.plot_widget.plot(levels,  filtered_avg_values, pen=pg.mkPen("b"))

    # метод возвращения средних значении уровней дерева
    def get_tree_avg_values(self, tree_view):
        # Создается пустой список level_values,
        # в котором будут значения узлов на каждом уровне дерева.
        level_values = []
        # с помощью метода calculate_avg_values
        # заполняем значениями узлов каждого уровня
        # начиная с корневого элемнта
        self.calculate_avg_values(
            tree_view.model().invisibleRootItem(), level_values, 0
        )
        # создаем новый список для среднийх значении каждого уровня
        # используя список котрый мы получили из метода calculate_avg_values
        avg_values = [
            np.mean(level) if level.any() else None for level in level_values
        ]
        return avg_values

    # метод формирования сиписка списков значении узлов
    def calculate_avg_values(self, tree_item, level_values, level):
        # если передонный уровень равени количеству уровней в списке
        # то дабавляем пустой массив
        if level == len(level_values):
            level_values.append(np.array([]))
        # получаем текст переданного узла
        node_text = tree_item.text()
        # если текст есть
        if node_text:
            try:
                # то пытаемся преобразовать в число
                value = int(node_text)
                # и добавить в массив в текущем уровне
                level_values[level] = np.append(level_values[level], value)
            # если получили ошибки то пропускаем этот узел
            except ValueError:
                pass
        # для каждого дочернего переданного узла
        # рекусрвино вызываем calculate_avg_values увеличивая уровнеь на 1
        for i in range(tree_item.rowCount()):
            self.calculate_avg_values(
                tree_item.child(i), level_values, level + 1
            )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TreeWindow()
    window.show()
    sys.exit(app.exec_())
