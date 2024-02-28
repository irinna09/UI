from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtCore import QSize, QDate
class Works:
    headers_params = {
        'Название': ['Номер', 'Наименование'],
        'Даты': ['Дата начала', 'Дата окончания'],
        'Объем работы': ['Единицы измерения', 'Объем работ',
                         'Кол-во персонала в смену', 'Число смен за период',
                         'Учитывать при расчете трудоемкости',
                         'Машина, количество маш.-ч.', 'Норма времени, чел.-ч.'],
        'Календарное планирование': ['Режим планирования', 'Процент выполнения'],
        'Норматив': ['Стиль', 'Номер по стандарту', 'Примечание', 'Состав']
    }

    def __init__(self):
        # здесь храним все выбранные работы
        self.list_selected_works = []

class Model:
    def gesn(self, data: dict):
        # Создание модели данных с двумя столбцами
        model_gesn = QStandardItemModel()
        model_gesn.setHorizontalHeaderLabels(["Наименование работ"])

        # Создание родительских элементов
        data_tree = []
        for key_1, values_1 in data.items(): # Раздел
            item_lvl_1 = QStandardItem(key_1)
            item_lvl_1.setEditable(False)
            data_tree.append(item_lvl_1)
            for key_2, values_2 in values_1.items(): # Подраздел
                item_lvl_2 = QStandardItem(key_2)
                item_lvl_2.setEditable(False)
                item_lvl_1.appendRow(item_lvl_2)
                for key_3, values_3 in values_2.items(): # Таблица
                    item_lvl_3 = QStandardItem(key_3)
                    item_lvl_3.setEditable(False)
                    item_lvl_2.appendRow(item_lvl_3)
                    for key_4, values_4 in values_3.items(): # Строки таблицы
                        item_lvl_4 = QStandardItem(key_4)
                        item_lvl_4.setEditable(False)
                        item_lvl_3.appendRow(item_lvl_4)

        for i in data_tree:
            model_gesn.appendRow([i])

        return model_gesn

    def current_work(self):
        model_current_work = QStandardItemModel()
        model_current_work.setHorizontalHeaderLabels(['Данные для вычислений', ''])
        # перебираем заголовки 1 уровня
        for header, subheaders in Works.headers_params.items():
            item_lvl_1 = QStandardItem(header)
            item_lvl_1.setEditable(False)
            # перебираем заголовки 2 уровня
            for subheader in subheaders:
                item_lvl_2 = QStandardItem(subheader)
                item_value = QStandardItem('')
                # если встречается в заголовке слово "дата", то отображаем как дату
                if "дата" in subheader.lower():
                    item_value = QStandardItem(QDate.currentDate().toString('dd.MM.yy'))
                elif "номер" == subheader.lower():
                    item_lvl_2.setEditable(False)

                item_lvl_1.appendRow([item_lvl_2, item_value])
            empty_item = QStandardItem('')
            empty_item.setEditable(False)

            model_current_work.appendRow([item_lvl_1, empty_item])

        return model_current_work

    def selected_works(self, works: Works):
        model_selected_works = QStandardItemModel()
        model_selected_works.setHorizontalHeaderLabels(['Номер', 'Наименование работ'])
        test =[]
        for work in works.list_selected_works:
            number = QStandardItem(str(work["Номер"]))
            name = QStandardItem(work["Наименование"])
            test.append(number)
            test.append(name)
            # model_selected_works.appendRow([number, name])
        for i in range(0,len(test),2):
            model_selected_works.appendRow([test[i], test[i+1]])

        return model_selected_works