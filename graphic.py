from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QSlider, QWidget,  QVBoxLayout, QLabel, QLineEdit, QHBoxLayout
from PyQt6.QtCore import Qt, QItemSelectionModel
from PyQt6.QtGui import QColor
from datetime import datetime, timedelta

class Graphic:
    """
    Он создает виджеты для графика в табличной форме и в виде рисунка.
    Методы:
        fill_dates - Заполнение первой строки датами
        fill_weekdays - Заполнение второй строки днями недели
        fill_data - заполнение таблицы данными
        fill_data_slider - обработка слайдера для управления видами таблицы
        change_sld - обработка событий слайдер
        on_selection_changed - Изменение цвета для выбранных ячеек


    """

    def __init__(self):
        self.sl_range = QSlider(Qt.Orientation.Horizontal)
        self.sl_range.setStyleSheet("""
                QSlider::handle {
                    background: #4F8E80;
                    border: 1px solid #4F8E80;
                    width: 13px;
                    margin: -2px 0; 
                    border-radius: 3px;
                }
                QSlider::groove {
                    background: white;
                }
                """)
        self.sl_range.setMaximum(1825)
        self.sl_range.setMinimum(0)
        self.sl_range.setValue(15)
        self.lbl_range = QLabel("Диапазон дней")
        self.le_range = QLineEdit("15")
        self.le_range.setMaximumWidth(50)
        self.le_range.textChanged.connect(self.change_sld)


        self.sl_range.valueChanged.connect(self.fill_data_slider)

        self.duration = 7
        self.start_date = datetime.now()

        # Создание и настройка таблицы
        self.table = QTableWidget(self)
        self.row = 8
        self.column = 15
        self.table.setRowCount(self.row)
        self.table.setColumnCount(self.column)

        # Заполнение таблицы данными
        self.fill_dates()
        self.fill_weekdays()
        self.fill_data()


        # self.highlight_duration()

        # Обработка сигнала изменения выделения
        self.table.selectionModel().selectionChanged.connect(self.on_selection_changed)

        self.hl_range = QHBoxLayout()
        self.hl_range.addWidget(self.lbl_range)
        self.hl_range.addWidget(self.sl_range)
        self.hl_range.addWidget(self.le_range)

        # self.vl_central.addLayout(self.hl_range)
        # self.vl_central.addWidget(self.table)




    def fill_dates(self):
        # Заполнение первой строки датами
        for i in range(self.column):
            date = (datetime.now() + timedelta(days=i)).date()
            self.table.setItem(0, i, QTableWidgetItem(str(date)))

    def fill_weekdays(self):
        # Заполнение второй строки днями недели
        for i in range(self.column):
            date = (datetime.now() + timedelta(days=i))
            self.table.setItem(1, i, QTableWidgetItem(date.strftime('%A')))

    def fill_data(self):
        for row in range(2, self.row):
            for column in range(0, self.column):
                self.table.setItem(row, column, QTableWidgetItem())

    def fill_data_slider(self):
        self.column = self.sl_range.value()
        self.le_range.setText(str(self.column))
        self.table.setRowCount(self.row)
        self.table.setColumnCount(self.column)
        self.fill_dates()
        self.fill_weekdays()
        self.fill_data()

    def change_sld(self):
        column_sld = int(self.le_range.text())
        if column_sld > self.sl_range.maximum():
            self.sl_range.setMaximum(column_sld)
        self.sl_range.setValue(column_sld)
        self.fill_data_slider()



    def on_selection_changed(self, selected, deselected):
        # Изменение цвета для выбранных ячеек
        first_date_str = self.table.item(0, 0).text()
        first_date = datetime.strptime(first_date_str, "%Y-%m-%d").date()
        print(type(first_date))
        selected_date_str = self.table.item(0, selected.indexes()[0].column()).text()
        selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d")
        print(type(selected_date))
        print(first_date, selected_date)
        print((selected_date + timedelta(days=1)).date())
        print(selected.indexes()[0].row(), "!")
        for a in range(0, self.column):
            self.table.item(selected.indexes()[0].row(), a).setBackground(QColor('#f7f7f7'))  # selected.indexes()[0].row()
        for i in range(0, self.duration):
            date = (selected_date + timedelta(days=i)).date()
            print(date)
            index_clm = (date - first_date).days
            if 0 <= index_clm < self.column:
                self.table.item(selected.indexes()[0].row(), index_clm).setBackground(QColor('#4F8E80')) #selected.indexes()[0].row()
#4F8E80

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()