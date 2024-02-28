import time
import requests
from bs4 import BeautifulSoup
import re
import json

class DownloadGESN:
    def __init__(self):
        # Инициализация базовых переменных
        self.gesn_2022 = {}
        self.url = "https://cs.smetnoedelo.ru"
        self.url_gesn_2022 = self.url + "/gesn2/"

    def fill_gesn_2022(self):
        # Заполнение данных ГЭСН 2022
        self.gesn_2022 = {}
        links_gesn_2022 = self.get_links_gesn_2022()
        for name_collection, link_collection in links_gesn_2022.items():
            print(name_collection)
            self.gesn_2022[name_collection] = {}
            links_collection = self.get_links_collection(self.url_gesn_2022 + link_collection)
            for razdel, podrazdels in links_collection.items():
                print("\t", razdel)
                self.gesn_2022[name_collection][razdel] = {}
                for podrazdel, tables in podrazdels.items():
                    print("\t\t", podrazdel)
                    self.gesn_2022[name_collection][razdel][podrazdel] = {}
                    for table, link in tables.items():
                        print("\t\t\t", table, "-->", link)
                        data = self.fill_section(links_collection)
                        self.gesn_2022[name_collection][razdel][podrazdel][table] = data

    def test_fill_gesn_2022(self):
            self.gesn_2022 = {}
            name_collection = "Мосты и трубы"
            link_collection = "sbor-30/"
            print(name_collection)
            self.gesn_2022[name_collection] = {}
            links_collection = self.get_links_collection(self.url_gesn_2022 + link_collection)
            for razdel, podrazdels in links_collection.items():
                print("\t", razdel)
                self.gesn_2022[name_collection][razdel] = {}
                for podrazdel, tables in podrazdels.items():
                    print("\t\t", podrazdel)
                    if podrazdel == "Опоры мостов на готовых фундаментах":
                        break
                    self.gesn_2022[name_collection][razdel][podrazdel] = {}
                    for table, link in tables.items():
                        print("\t\t\t", table, "-->", link)
                        data = self.fill_section(links_collection)
                        self.gesn_2022[name_collection][razdel][podrazdel][table] = data

    def save_gesn(self, data, file_name="ГЭСН2022"):
        # Сохранение данных в формате JSON
        with open(f'{file_name}.json', 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    def get_links_gesn_2022(self):
        # Получение ссылок на ГЭСН 2022
        response = requests.get(self.url_gesn_2022)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            gesn_2022 = {}  # Ссылки на сборники ГЭСН 2022
            for collection in soup.find("ul", class_="29 pl-3").find_all("li"):
                name = collection.text.split(" ")[0]  # Сборник 01. Земляные работы
                name = name.split(".")[1].strip()  # Земляные работы
                gesn_2022[name] = collection.find("a").get("href")
        else:
            print("Не удалось получить страницу с ГЭСН 2022")
        return gesn_2022

    def get_links_collection(self, url="https://cs.smetnoedelo.ru/gesn2/sbor-30/"):
        # Получение ссылок на коллекции ГЭСН 2022
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")

            razdels = {}
            last_razdel = ""
            last_podrazdel = ""
            name = []
            for razdel in soup.find_all("li"):
                if "Раздел" in razdel.text:
                    # название заканчивается спец символом
                    match = re.search(' ', razdel.text)
                    name.append(razdel.text[0:match.start()])
                    if len(name) != 0:
                        # Раздел 1. Железобетонные и бетонные конструкции мостов и труб
                        last_razdel = razdel.text[0:match.start()]
                        # Железобетонные и бетонные конструкции мостов и труб
                        last_razdel = last_razdel[last_razdel.find(". ") + 2:].strip()
                        razdels[last_razdel] = {}
                    else:
                        print("Ошибка")
                elif "Подраздел" in razdel.text:
                    # название заканчивается спец символом
                    match2 = re.search(' ', razdel.text)
                    # Подраздел 1.1. Разработка грунта экскаваторами в отвал
                    last_podrazdel = razdel.text[0:match2.start()]
                    # Разработка грунта экскаваторами в отвал
                    last_podrazdel = last_podrazdel[last_podrazdel.find(". ") + 2:].strip()
                    razdels[last_razdel][last_podrazdel] = {}
                elif "Таблица" in razdel.text:
                    if last_razdel == "":
                        last_razdel = "Раздел"
                        razdels[last_razdel] = {}
                    if len(razdels[last_razdel]) == 0:
                        last_podrazdel = "Подраздел"
                        razdels[last_razdel][last_podrazdel] = {}
                    index_start = razdel.text.find(". ") + 2
                    index_end = razdel.text.find(" ")
                    name_table = razdel.text[index_start:index_end]
                    razdels[last_razdel][last_podrazdel][name_table] = razdel.find("a").get("href")

        else:
            print(":'( Не удалось получить доступ к сбонику")
        #for k, v in razdels.items():
            #print(k)
            #for k2, v2 in v.items():
                #print("\t", k2)
                #for v3 in v2:
                    #print("\t\t\t", v3)
        return razdels

    def fill_section(self, razdels):
        # Заполнение секций данными
        data = {}
        for razdel, podrazdels in razdels.items():
            print(razdel)
            data[razdel] = {}
            for podrazdel, tables in podrazdels.items():
                print("\t", podrazdel)
                data[razdel][podrazdel] = {}
                for table, link in tables.items():
                    url = "https://cs.smetnoedelo.ru" + link
                    response = requests.get(url)
                    works = {} #вложенный словарь
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, "html.parser")
                        work_name = soup.find("h1").text
                        work = []
                        #work.append(tag_h1.text)
                        tag_table = soup.find("table")

                        # парсим заголовки таблицы
                        head = tag_table.find("thead").find("tr")
                        rows = []
                        for column in head.find_all("th"):
                            rows.append(column.text.strip())
                        # добавляем доп. колонку с единицами измерения
                        rows.append("Единицы измерения")
                        work.append(rows)

                        # парсим содержимое таблицы
                        tag_tr = tag_table.find_all("tr")
                        works2 = {}
                        for row in tag_tr:
                            rows = []
                            i = 0
                            for column in row.find_all("td"):
                                i = i + 1
                                cell = column.text.strip()
                                rows.append(cell)
                                if i == 2:
                                    name_work2 = column.text.strip()
                                    works2[name_work2] = rows
                            if len(rows) > 0:
                                # Добавляем единицы измерения, если есть
                                if "—" in rows[1]:
                                    index = rows[1].find("—")
                                    rows.append(rows[1][index + 2:].strip())
                                    rows[1] = rows[1][:index].strip()
                                else:
                                    rows.append("")
                                # Добавляем шифр
                                work.append(rows)
                        print(works2)
                        works[work_name] = works2
                        data[razdel][podrazdel][table] = works
                        #for k, v in works.items():
                            #print("\t\t\t\t", k, "\t\t\t\t", v)
                        #print()


if __name__ == "__main__":
    test = DownloadGESN()

    # Скачать ВЕСЬ ГЭСН 2022
    # test.fill_gesn_2022()
    # test.save_gesn(test.gesn_2022)

    # Скачать только Мосты
    #test.test_fill_gesn_2022()
    #test.save_gesn(test.gesn_2022)
    test.fill_section(test.get_links_collection())