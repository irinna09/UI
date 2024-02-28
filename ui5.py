# pip install PyQt6 PySide6 qt-material json
import json
from PySide6 import QtWidgets
from qt_material import apply_stylesheet, list_themes, QtStyleTools

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

from Model import Model, Works
from graphic import Graphic
from KPP import Workname
from Diagrama import Diagram

import openpyxl



class DateEditDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        try:
            # проверяем ячейку слева от выбранной
            leftIndex = index.siblingAtColumn(index.column() - 1)
            # Проверяем, является ли полученный индекс действительным
            if leftIndex.isValid():
                # Получаем данные ячейки слева
                leftData = leftIndex.data().lower()
                # если в ней содержится слово дата, то редактируй ее как дату
                if "дата" in leftData:
                    editor = QDateEdit(parent)
                    editor.setCalendarPopup(True)
                    editor.setDateRange(QDate(2000, 1, 1), QDate(2050, 12, 31))
                    return editor
        except Exception as e:
            print(e)
        # иначе редактируй ячейку как обычно
        return super().createEditor(parent, option, index)


class UI(QMainWindow, QtStyleTools, Graphic, Diagram):
    def __init__(self):
        super().__init__()
        Graphic.__init__(self)
        Diagram.__init__(self)

        self.tab_index = 0

        self.resize(1200, 900)
        self.setWindowTitle('График производственных работ')
        self.config = self.check_config()  #check_config-позволяет проверить изменения в файле конфигурации перед запуском Home Assistant.

        self.central_widget = QWidget()
        self.vl_central = QVBoxLayout()
        self.central_widget.setLayout(self.vl_central)
        self.setCentralWidget(self.central_widget)

        # Меню
        self.menu_bar = QMenuBar()
        self.setMenuBar(self.menu_bar)

        self.menu_file = self.menu_bar.addMenu("Файл")
        self.menu_setting = self.menu_bar.addMenu("Настройки")

        self.action_save = QAction("Сохранить")
        self.menu_file.addAction(self.action_save)
        self.action_save.triggered.connect(self.save_file)
        self.action_open = QAction("Открыть")
        self.menu_file.addAction(self.action_open)
        self.action_open.triggered.connect(self.open_file)

        # self.action_view = self.menu_setting.addMenu("Отображение")
        self.action_theme = self.menu_setting.addMenu("Изменить тему")
        self.action_theme_items = []
        for theme in list_themes():
            if "yellow" in theme:
                continue
            theme = theme.replace("_", " ")
            theme = theme.replace(".xml", "")
            self.action_theme_items.append(QAction(theme))
            self.action_theme.addAction(self.action_theme_items[-1])
            self.action_theme_items[-1].triggered.connect(self.choose_theme)

        # Создание виджета вкладок
        self.tabs = QTabWidget()
        self.tabs.currentChanged.connect(self.change_tab)
        self.vl_central.addWidget(self.tabs)

        # Вкладка Работы
        self.tab1 = QWidget()
        self.tabs.addTab(self.tab1, "Работы")
        self.hl_works = QHBoxLayout()
        self.tab1.setLayout(self.hl_works)

        # Вкладка График
        self.tab2 = QWidget()
        self.tabs.addTab(self.tab2, "График")
        self.hl_graphic = QHBoxLayout()


        self.vl_works_left = QVBoxLayout()
        self.vl_works_left.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.vl_works_right = QVBoxLayout()
        self.hl_works.addLayout(self.vl_works_left)
        self.hl_works.addLayout(self.vl_works_right)

        # выбранные работы
        self.tr_select_work = QTreeView(self) #QTreeView - реализует иерархический список
        self.vl_works_left.addWidget(self.tr_select_work)
        self.model_select_work = QStandardItemModel() #QStandardItemModel - реализует двумерную (таблица) и иерархическую модели
        self.model_select_work.setHorizontalHeaderLabels(["Номер", "Наименование работ"]) #setHorizontalHeaderLabels-задает заголовки столбцов
        self.tr_select_work.setModel(self.model_select_work)
        self.tr_select_work.clicked.connect(self.event_choose_work)
        self.counter_works = 1

        self.btn_add = QPushButton("Добавить")
        self.btn_add.clicked.connect(self.add_current_work)
        self.btn_change = QPushButton("Изменить")
        self.btn_change.clicked.connect(self.change_selected_work)
        self.btn_del = QPushButton("Удалить ")
        self.btn_del.clicked.connect(self.del_selected_work)
        self.hl_btn = QHBoxLayout()
        self.hl_btn.setAlignment(Qt.AlignmentFlag.AlignRight) #setAlignment - задает выравнивание сцены
        self.hl_btn.addWidget(self.btn_add)
        self.hl_btn.addWidget(self.btn_change)
        self.hl_btn.addWidget(self.btn_del)
        self.vl_works_left.addLayout(self.hl_btn)

        # работы в ГЭСН
        self.tr_gesn = QTreeView(self) #QTreeView - реализует иерархический список
        # self.model_select_work.setHorizontalHeaderLabels(["ГЭСН"])
        self.vl_works_left.addWidget(self.tr_gesn)

        # Создаем модель с для текущей работы (выбранной в ГЭСН)
        self.model = Model().current_work()

        # Создаем и настраиваем QTreeView
        self.tree_view = QTreeView()

        self.tree_view.setModel(self.model)

        self.tree_view.expandAll()  # Разворачиваем все узлы. expandAll() - отображает все дочерние элементы.
        # Устанавливаем делегат для второго столбца
        self.delegate = DateEditDelegate() #За редактирование данных в представлении отвечает делегат
        self.tree_view.resizeColumnToContents(0) #для изменения размеров столбца в таблице или виджете так, чтобы он соответствовал содержимому ячеек в этом столбце
        self.tree_view.setItemDelegateForColumn(1, self.delegate) #устанавливает делегат self.delegate для столбца с индексом 1 в self.tree_view.
        self.vl_works_right.addWidget(self.tree_view)
        self.tree_view.setMaximumWidth(450)
        self.tree_view.setStyleSheet("QTreeView::item { border: 0.5px solid lightgray; }")
        self.tree_view.resizeColumnToContents(0)

        self.add_gesn()
        self.works = Works()

        self.tab2.setLayout(self.hl_graphic)
        self.vl = QVBoxLayout()
        self.vl2 = QVBoxLayout()
        self.hl_graphic.addLayout(self.vl2)
        self.hl_graphic.addLayout(self.vl)

        self.vl.addWidget(self.table)
        self.vl.addLayout(self.hl_range)

        #добавляю график, три кнопки. Кнопки таблица и график взаимоисключ
        self.vl.addWidget(self.canvas)
        self.canvas.hide()
        self.group_box = QGroupBox("Group Title")
        self.layout = QHBoxLayout()
        self.button1_save = QPushButton("Сохранить")
        self.button1_save.clicked.connect(self.save_graphic_or_tabl)
        self.button2_tabl = QPushButton("Таблица")
        self.button2_tabl.clicked.connect(self.look_tabl)
        self.button3_graphic = QPushButton("График")
        self.button3_graphic.clicked.connect(self.look_graphic)
        self.button_group = QButtonGroup()
        self.button_group.addButton(self.button2_tabl)
        self.button_group.addButton(self.button3_graphic)
        self.button_group.setExclusive(True)
        self.layout.addWidget(self.button1_save)
        self.layout.addWidget(self.button2_tabl)
        self.layout.addWidget(self.button3_graphic)
        self.group_box.setLayout(self.layout)
        self.vl2.addWidget(self.group_box)


    def save_graphic_or_tabl(self):
        #filename, _ = QFileDialog.getSaveFileName(self, 'Сохранить файл', '', 'Excel Files (*.xlsx)')
        if self.table.isVisible():
            filename, _ = QFileDialog.getSaveFileName(self, 'Сохранить файл', '', 'Excel Files (*.xlsx)')
            if filename: #используется для проверки того, был ли пользователем выбран файл для сохранения перед нажатием кнопки "Сохранить"
                workbook = openpyxl.Workbook()
                sheet = workbook.active
                for row in range(self.table.rowCount()):
                    for col in range(self.table.columnCount()):
                        item = self.table.item(row, col)
                        sheet.cell(row=row + 1, column=col + 1, value=item.text())

                workbook.save(filename)
        elif self.canvas.isVisible():
            file_name, _ = QFileDialog.getSaveFileName(self, 'Сохранить график', '', 'PNG Files (*.png)')
            if file_name:
                self.figure.savefig(file_name)



    def look_tabl(self):
        try:
            self.table.show()
            self.lbl_range.show()
            self.sl_range.show()
            self.le_range.show()
            self.canvas.hide()
        except Exception as e:
            print(f"An error occurred: {e}")

    def look_graphic(self):
        try:
            self.canvas.show()
            self.table.hide()
            self.lbl_range.hide()
            self.sl_range.hide()
            self.le_range.hide()

        except Exception as e:
            print(f"An error occurred: {e}")



    def change_tab(self, index):
        self.tab_index = index
        try:
            if index == 1:
                self.vl2.insertWidget(0, self.tr_select_work)
            elif index == 0 and hasattr(self, 'vl_works_left'):
                self.vl_works_left.insertWidget(0, self.tr_select_work)
        except Exception as e:
            print(e)



    def save_file(self, file_name="ГЭСН2022"):
        # Сохранение данных в формате JSON
        file_dialog = QFileDialog(self)
        file_path, _ = file_dialog.getSaveFileName(filter="Текстовый файл (*.json);;All Files (*)")
        if file_path:
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(self.works.list_selected_works, file, ensure_ascii=False)
                QMessageBox.information(self, "Сохранено", "Текст успешно сохранен.")

    def open_file(self):
        file_dialog = QFileDialog(self)
        file_path, _ = file_dialog.getOpenFileName(filter="Текстовый файл (*.json);;All Files (*)")
        test = []
        data = {}
        if file_path:
            with open(file_path, "r", encoding="utf-8") as file:
                data = file.read()
                try:
                    my_list = json.loads(data)
                    #print(my_list)
                    self.works.list_selected_works.clear()
                    for i in my_list:
                        self.works.list_selected_works.append(i)
                    self.model_select_work = Model().selected_works(self.works)
                    self.tr_select_work.setModel(self.model_select_work)
                except json.JSONDecodeError as e:
                    print(f"Ошибка при загрузке JSON: {e}")

    def event_choose_work(self):
        """
         Выбор работы из списка
        """
        if self.tab_index == 0:
            selection_model = self.tr_select_work.selectionModel() #получения модели
            # Получаем список выделенных индексов
            selected_indexes = selection_model.selectedIndexes() #возвращает список индексов выбранных элементов в виджете
            if selected_indexes:
                number = selected_indexes[0].data()  #data()-доступ к данным этого индекса
                print(number) #?????????????????
                for i in range(len(self.works.list_selected_works)):
                    if self.works.list_selected_works[i]["Номер"] == int(number):
                        # Заполнение данных о выбранной работе в модель для отображения
                        for key, value in self.works.list_selected_works[i].items():
                            foundIndex = self.findIndexByValue(self.model, key)
                            rightIndex = foundIndex.siblingAtColumn(foundIndex.column() + 1)
                            self.model.setData(rightIndex,
                                               value,
                                               Qt.ItemDataRole.DisplayRole)
                        break
        elif self.tab_index == 1:
            selection_model = self.tr_select_work.selectionModel()  # получения модели
            # Получаем список выделенных индексов
            selected_indexes = selection_model.selectedIndexes()  # возвращает список индексов выбранных элементов в виджете
            if selected_indexes:
                number = selected_indexes[0].data()  # data()-доступ к данным этого индекса
                print(number)

    def change_selected_work(self):
        """
        Изменение данных выбранной работы
        """
        data = {}
        # Сбор данных из модели для текущей выбранной работы
        for header, subheaders in self.works.headers_params.items():
            for subheader in subheaders:
                found_index = self.findIndexByValue(self.model, subheader)
                right_index = found_index.siblingAtColumn(found_index.column() + 1)
                data[subheader] = right_index.data()
        flag_can_add = True
        if data["Номер"] == "":
            flag_can_add = False
        if flag_can_add:
            # Обновление данных о работе в списке выбранных работ
            for i in range(len(self.works.list_selected_works)):
                work = self.works.list_selected_works[i]
                if int(data["Номер"]) == int(work["Номер"]):
                    for key, value in work.items():
                        self.works.list_selected_works[i][key] = data[key]
                    break
            # Обновление модели для отображения изменений
            self.model_select_work = Model().selected_works(self.works)
            self.tr_select_work.setModel(self.model_select_work)

    def del_selected_work(self):
        """
        Удаление выбранной работы из списка
        """
        selection_model = self.tr_select_work.selectionModel()
        # Получаем список выделенных индексов
        selected_indexes = selection_model.selectedIndexes()
        if selected_indexes:
            number = selected_indexes[0].data()
            for i in range(len(self.works.list_selected_works)):
                if self.works.list_selected_works[i]["Номер"] == int(number):
                    self.works.list_selected_works.pop(i)
                    # Обновление модели после удаления
                    self.model_select_work = Model().selected_works(self.works)
                    self.tr_select_work.setModel(self.model_select_work)
                    break

    def add_current_work(self):
        """
        Добавление текущей работы в список выбранных

        """
        data = {}
        for header, subheaders in self.works.headers_params.items():
            for subheader in subheaders:
                found_index = self.findIndexByValue(self.model, subheader)
                right_index = found_index.siblingAtColumn(found_index.column() + 1)
                data[subheader] = right_index.data()
        flag_can_add = True
        for work in self.works.list_selected_works:
            if work["Номер"] == data["Номер"]:
                flag_can_add = False
        if data["Номер"] == "":
            flag_can_add = False
        if flag_can_add:
            self.works.list_selected_works.append(data)
            # Обновление модели для отображения новой работы
            self.model_select_work = Model().selected_works(self.works)
            self.tr_select_work.setModel(self.model_select_work)
            try:
                #workname = Workname()
                names = list(self.works.list_selected_works[-1].keys())
                example = list(self.works.list_selected_works[-1].values())
                data2 = [example]
                work1 = Workname(names, data2)
                print(names)
                print(example)
                print(work1.calc(work1.example_dict["Устройство подушек под фундаменты опор мостов: щебеночных"]))
            except Exception as e:
                print(e)
            #names = "Наименование работ\tОбоснование норм\tКол-во персонала/машин в смену\tЕд. изм.\tНорма затрат труда, чел.-ч.\tОбъем V"
            #example_1 = "Монтаж плит\t30-018-01-1\t6\t1\t2.76\t40.6"
            #example_2 = "Устройство обмазочной гидроизоляции\tЕ4-3-184\t4\t1 м3\t0.27\t78"
            #example_3 = "Обсыпка трубы\tЕ2-1-34 5\t100 м3\t0.49\t2.1"
            #names = names.split("\t")
            #data = [example_1.split("\t"), example_2.split("\t"), example_3.split("\t")]
            #work1 = Workname(names,data)
            #print(work1.calc(work1.example_dict["Монтаж плит"]))
        #print(data)

    def add_gesn(self):
        # Создание родительских элементов
        with open("ГЭСН.json", "r", encoding="utf-8") as file:
            data = json.load(file)
        # Создаем ветки ГЭСН на основе данных из файла
        self.model_gesn = Model().gesn(data)
        self.model_gesn.setHorizontalHeaderLabels(["Наименование работ"])

        # Привязка модели к дереву отображения
        self.tr_gesn.setModel(self.model_gesn)
        self.tr_gesn.resizeColumnToContents(0)
        self.tr_gesn.clicked.connect(self.add_work)

    def getParentDepth(self, index: QModelIndex, depth=0):
        """
        Определение глубины вложенности элемента в дереве
        """
        if not index.parent().isValid():
            return depth
        else:
            return self.getParentDepth(index.parent(), depth + 1)
            #print(depth)

    def findIndexByValue(self, model, value, parent=QModelIndex()):
        """
        Поиск индекса элемента по его значению.
        Рекурсивный поиск по всем элементам модели.
        """
        for row in range(model.rowCount(parent)):
            for column in range(model.columnCount(parent)):
                index = model.index(row, column, parent)
                if model.data(index) == value:
                    return index
                # Если у элемента есть дочерние элементы, ищем рекурсивно в них
                if model.hasChildren(index):
                    # функция рекурсивно вызывает себя внутри себя
                    foundIndex = self.findIndexByValue(model, value, index)
                    if foundIndex:
                        return foundIndex
        return None

    def add_work(self, index):
        # Добавление работы из ГЭСН в список выбранных работ
        if index.isValid():
            # Получение индекса первой колонки текущей строки
            item = self.model_gesn.index(index.row(), 0, index.parent())
            current_index = item.sibling(index.row(), 0)
            current_value = self.model_gesn.data(current_index)

            # узнаем, на каком уровне вложения мы находимся
            depth = self.getParentDepth(index)
            # Проверка глубины для определения, является ли элемент работой
            if depth == 3:
                work_index = index.parent()
                work_item = self.model_gesn.itemFromIndex(work_index)
                work_name = work_item.text()

                podrazdel_index = work_index.parent()
                podrazdel_item = self.model_gesn.itemFromIndex(podrazdel_index)
                podrazdel_name = podrazdel_item.text()

                razdel_index = podrazdel_index.parent()
                razdel_item = self.model_gesn.itemFromIndex(razdel_index)
                razdel_name = razdel_item.text()

                with open("ГЭСН.json", "r", encoding="utf-8") as file:
                    data = json.load(file)
                print(data[razdel_name][podrazdel_name][work_name][current_value])

                # Встака данных
                foundIndex = self.findIndexByValue(self.model, "Номер по стандарту")
                rightIndex = foundIndex.siblingAtColumn(foundIndex.column() + 1)
                self.model.setData(rightIndex,
                                   data[razdel_name][podrazdel_name][work_name][current_value][0],
                                   Qt.ItemDataRole.DisplayRole)

                foundIndex = self.findIndexByValue(self.model, "Наименование")
                rightIndex = foundIndex.siblingAtColumn(foundIndex.column() + 1)
                self.model.setData(rightIndex,
                                   data[razdel_name][podrazdel_name][work_name][current_value][1],
                                   Qt.ItemDataRole.DisplayRole)

                foundIndex = self.findIndexByValue(self.model, "Норма времени, чел.-ч.")
                rightIndex = foundIndex.siblingAtColumn(foundIndex.column() + 1)
                self.model.setData(rightIndex,
                                   data[razdel_name][podrazdel_name][work_name][current_value][2],
                                   Qt.ItemDataRole.DisplayRole)

                foundIndex = self.findIndexByValue(self.model, "Машина, количество маш.-ч.")
                rightIndex = foundIndex.siblingAtColumn(foundIndex.column() + 1)
                self.model.setData(rightIndex,
                                   data[razdel_name][podrazdel_name][work_name][current_value][3],
                                   Qt.ItemDataRole.DisplayRole)

                foundIndex = self.findIndexByValue(self.model, "Единицы измерения")
                rightIndex = foundIndex.siblingAtColumn(foundIndex.column() + 1)
                self.model.setData(rightIndex,
                                   data[razdel_name][podrazdel_name][work_name][current_value][4],
                                   Qt.ItemDataRole.DisplayRole)

                if len(self.works.list_selected_works) > 0:
                    self.counter_works = self.works.list_selected_works[-1]["Номер"] + 1
                else:
                    self.counter_works = 1

                foundIndex = self.findIndexByValue(self.model, "Номер")
                rightIndex = foundIndex.siblingAtColumn(foundIndex.column() + 1)
                self.model.setData(rightIndex,
                                   self.counter_works,
                                   Qt.ItemDataRole.DisplayRole)
                self.tr_gesn.selectionModel().clearSelection()

    def choose_theme(self):  # выбрать тему оформления
        # Получите объект QAction, который вызвал событие
        theme = self.sender()

        # Получите текст из свойства 'text' объекта QAction
        if theme:
            theme = theme.text().replace(" ", "_")
            theme += ".xml"
            self.apply_new_theme(theme)

    def apply_new_theme(self, theme):
        self.apply_stylesheet(self, theme)
        # настраиваем ширину колонки
        self.tree_view.resizeColumnToContents(0)
        self.change_config({"theme": theme})

    def check_config(self):
        import os
        # считываем конфигурационный файл
        try:
            path = "config.json"
            # если путь существует и он ведет к файлу, то прочти его
            if os.path.exists(path) and os.path.isfile(path):
                with open(path, 'r') as file:
                    data = json.load(file)
            else:
                raise ValueError("Ошибка в конфигурационном файле")
        except Exception as e:
            print(f"Error - {e}")
            data = {"theme": "dark_teal.xml"}
            with open(path, 'w') as file:
                json.dump(data, file)
        return data

    def change_config(self, items):
        data = self.check_config()
        for key, value in items.items():
            data[key] = value
        path = "config.json"
        with open(path, 'w') as file:
            json.dump(data, file)


if __name__ == "__main__":
    app = QApplication([])
    window = UI()
    apply_stylesheet(app, theme=window.check_config()["theme"])  # theme=config["theme"]
    window.show()
    app.exec()




"""
Шпоры для Иры:

filename, _ = QFileDialog.getSaveFileName(self, 'Сохранить файл', '', 'Excel Files (*.xlsx)')

Эта строка кода использует стандартный диалоговый виджет QFileDialog 
из библиотеки PyQt для отображения диалогового окна сохранения файла.

1. filename: Этот параметр содержит путь к выбранному файлу.

2. _: Это переменная, которая используется для игнорирования второго 
возвращаемого значения из метода getSaveFileName(). 

3. QFileDialog.getSaveFileName(self, 'Сохранить файл', '', 'Excel Files (*.xlsx)'): 
Это вызов метода getSaveFileName() класса QFileDialog, который открывает диалоговое окно сохранения файла. 
   - self: Ссылка на текущий объект, который обычно используется внутри классов PyQt.
   - 'Сохранить файл': Это заголовок диалогового окна сохранения файла.
   - '': Это начальный путь к файлу, который будет отображаться при открытии диалогового окна.
   - 'Excel Files (*.xlsx)': Это фильтр файлов, который ограничивает типы файлов, которые 
   пользователь может выбирать при сохранении. 
"""

