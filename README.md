
# TREE_NUMS

Описание проекта: Этот проект представляет собой программу для обработки данных из дерева и сохранения их в файл формата HDF5.
Окно содержит дерево, в узлы которого можно класть только числа и график под деревом. Редактировать через двойной клик можно только листья дерева.
Добавление узлов происходит с использованием текстового поля и кнопки, по нажатию на которую к выделенному элементу дерева будет добавляться новый дочерний узел.
Удаление выделенных узлов происходит по нажатию на другую кнопку. Значения в каждом узле кроме листьев пересчитываются из значений дочерних элементов этого узла после изменений (редактирование/добавление/удаление) узла как сумма значений дочерних элементов. Узлы второго уровня заливаются красным или зеленым цветом в зависимости от того, положительные они или отрицательные. При изменении какого-либо узла дерева перерисовывается график зависимости двух величин: по оси Y - среднее значение на уровне, по оси X уровень.

Кнопки для управления: для сохранения данных дерева в hdf; загрузки его из hdf; для создания дерева случайной глубины и заполнения листьев случайными значениями.

Проект упакован в файл .exe.

## Установка

1. Клонируйте репозиторий: `git clone https://github.com/Ruslandkadyrov/TreeNums`
2. Установите зависимости: `pip install -r requirements.txt`

## Использование

1. Запустите программу.
2. Кнопкой "Создать дерево случайной глубины" добавьте дерево
3. Кнопкой "Заполнить пустые листья дерева случайными значениями" заполните дерево значениями
4. Кнопкой "Сохранить дерево в HDF5" можно сохранить дерево в формате HDF5 в текущую дерикторию
5. Кнопкой "Загрузить дерево из HDF5" можно загрузить дерево из текущей дериктории из формата HDF5

## Автор

Автор: Кадыров Руслан Ринатович
