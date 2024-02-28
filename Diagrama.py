import sys

import pandas
from PyQt6.QtWidgets import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates
import pandas as pd

class Diagram():
    def __init__(self):
        try:
            #super().__init__()


            self.main_widget = QWidget(self)
            self.setCentralWidget(self.main_widget)
            self.layout = QVBoxLayout(self.main_widget)


            self.figure = Figure()
            self.canvas = FigureCanvas(self.figure)
            self.draw_graphic()

            self.h = QHBoxLayout()
            self.lb = QLabel("Ghbdtn")
            self.layout.addLayout(self.h)
            self.h.addWidget(self.lb)
            self.h.addWidget(self.canvas)


        except Exception as error:
            print(error)


    def draw_graphic(self):

        data = {"Работы": ['Устройство подушек', 'Устройство бетонных', 'Устройство деревянного перекрытия котлованов', 'Устройство сборных фундаментов', 'Устройство монолитных фундаментов'],
                "Начало работ": ["04.12.2024", "04.13.2024", "04.14.2024", "04.13.2024", "04.12.2024"],
                "Конец работ": ["04.14.2024", "04.15.2024", "04.19.2024", "04.20.2024", "04.13.2024"]}
        df = pandas.DataFrame(data)
        df["Начало работ"] = pd.to_datetime(df["Начало работ"])
        df["Конец работ"] = pd.to_datetime(df["Конец работ"])
        print(df)
        ax = self.figure.add_subplot(122)
        for index, row in df.iterrows():
            ax.hlines(y=index, xmin=row["Начало работ"], xmax=row["Конец работ"], lw=4, color="black")
            ax.plot([row["Начало работ"], row["Конец работ"]], [index, index], "D", color="green")

        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m'))
        ax.xaxis.set_major_locator(mdates.DayLocator())
        ax.set_yticks(range(len(df)))
        ax.set_yticklabels(df["Работы"])
        ax.set_xlabel('Дата')
        ax.set_ylabel('Работа')
        ax.set_title('График производственных работ по устройству ...')



if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())

