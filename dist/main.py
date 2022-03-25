import sys

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton
from PyQt5.QtWidgets import QMainWindow, QLabel, QLineEdit, QInputDialog, \
    QTableWidgetItem, QMessageBox, QSpinBox, QHeaderView, QHBoxLayout, \
    QGraphicsView, QGraphicsScene, QListWidget, QComboBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtChart import QChart, QChartView, QPieSeries, QPieSlice
from PyQt5 import uic, QtGui
import sqlite3
import datetime as dt
import matplotlib.pyplot as plt
from PyQt5.QtCore import Qt


def update_history(summ, event):
    '''
    Обновляет историю платежей, представленую в классе History
    :param summ: сумма изменения счета
    :param event: одна из 2 операций: "зачисление", "покупка акций"
    :return:
    '''
    summ = summ
    hour = dt.datetime.now().time().hour
    minute = dt.datetime.now().time().minute
    second = dt.datetime.now().time().second
    time = f'{hour}-{minute}-{second}'
    data = dt.date.today()
    event = event
    con = sqlite3.connect('history1.db')
    cur = con.cursor()

    que = f'''INSERT INTO history(Event, summ, data, time) 
    VALUES('{event}', {summ}, '{data}', '{time}')'''
    result = cur.execute(que).fetchall()

    con.commit()
    con.close()


def save(name, score, index):
    '''
    Сохраняет данные пользователя в файл
    :param name: имя пользователя, сохраняется также при изменении имени
    :param score: сумма на ссчету пользователя, обновляется при зачислении или покупки
    :param index: индекс в таблице истории платежей
    :return:
    '''
    with open("Info.txt", mode='w', encoding='utf-8') as g:
        g.write(name)
        g.write('\n')
        g.write(str(score))
        g.write('\n')
        g.write(str(index))


def checked_data(date):
    '''
    Проверяет изменилась ли дата с последнего открытия приложения
    :param date: текущая дата
    :return: количество дней с последнего открытия приложения
    '''
    with open('data.txt', mode='r', encoding='utf-8') as f:
        data_now = f.readline().rstrip('\n').split(';')
        data_now = dt.date(int(data_now[0]), int(data_now[1]), int(data_now[2]))

    if data_now < date:
        return (date - data_now).days
    else:
        return 0


class MainWindow(QMainWindow):
    '''
    Главное окно, с переходами в остальные классы
    '''

    def __init__(self):
        super().__init__()
        uic.loadUi('формы/Главное окно.ui', self)
        self.setGeometry(100, 100, 713, 555)
        self.setWindowTitle('Кошелек')
        self.setWindowIcon(QtGui.QIcon('icon.png'))
        self.status = False
        self.index = 1
        with open("Info.txt", mode='r', encoding='utf-8') as f:
            str_1 = f.readline()
            self.name = str_1.rstrip('\n')
            self.hello.setText(f'Приветствую, {self.name}!')
            str_2 = f.readline()
            self.score = eval(str_2.rstrip('\n'))
            self.balance.setText(f'На вашем счете: {round(self.score, 2)} @')
            str_3 = f.readline()
            self.index = int(str_3.rstrip('\n'))

        self.days = checked_data(dt.date.today())
        self.update_balance(self.days)
        self.update_data()

        self.change_name.clicked.connect(self.run)
        self.notifications.clicked.connect(self.notic)
        self.add_account.clicked.connect(self.add)
        self.all.clicked.connect(self.alll)
        self.change_name.clicked.connect(self.my_event)
        self.calculator.clicked.connect(self.diary)
        self.help.clicked.connect(self.get_help)
        self.investments.clicked.connect(self.invest)
        self.payment_history.clicked.connect(self.history)

    def notic(self):
        '''
        Открываает форму с уведомлениями
        :return:
        '''
        self.noticc = Notifications(self, self.lst)
        self.noticc.show()

    def my_event(self):
        pass

    def get_help(self):
        '''
        Открываает форму О проекте
        :return:
        '''
        self.help = AboutProject(self, 'данных нет')
        self.help.show()

    def update_balance(self, days):
        '''
        Обновляяет сумму, добавляя диведенды, полученные от акций
        :param days: количество дней с последнего открытия приложения
        :return:
        '''
        data = f'{dt.date.today().year}-{dt.date.today().month}-{dt.date.today().day}'
        with open('file.txt', mode='r', encoding='utf-8') as f:
            f = f.readline().rstrip('\n').split(';')
            sum_invest = sum([float(i) for i in f])

        self.score += round(0.01 * sum_invest * days, 2)
        self.lst = []
        with open('notic.txt', mode='r', encoding='utf-8') as f:
            a = f.readline().rstrip('\n').split(';')
            b = f.readline().rstrip('\n').split(';')
            a = [float(i) for i in a if i != '']
            for i in range(len(a)):
                self.lst.append((a[i], b[i]))
        if days:
            self.lst.append((round(0.01 * sum_invest * days, 2), data))
        self.balance.setText(f'На вашем счете: {self.score} @')

    def update_data(self):
        '''
        Обновляет дату последнего открытия приложения, меняя на текущую
        :return:
        '''
        with open('data.txt', mode='w', encoding='utf_8') as g:
            year = dt.date.today().year
            month = dt.date.today().month
            day = dt.date.today().day
            g.write(f'{year};{month};{day}')
        with open('notic.txt', mode='w', encoding='utf-8') as g:
            a = [str(i[0]) for i in self.lst]
            b = [i[1] for i in self.lst]
            g.write(';'.join(a))
            g.write('\n')
            g.write(';'.join(b))

    '''
    Следуюшие 4 метода открывают формы представленных классов
    '''

    def alll(self):
        with open('file.txt', mode='r', encoding='utf-8') as f:
            f = f.readline().rstrip('\n').split(';')
            f = [float(i) for i in f]

        self.al = All(self, [self.score, sum(f)])
        self.all.show()

    def diary(self):
        self.diary = Diary(self, 'нет данных')
        self.diary.show()
        self.hide()

    def history(self):
        self.history = History(self, 'данных нет')
        self.history.show()
        self.hide()

    def invest(self):
        self.investt = Invest(self, [self.name, self.score, self.index])
        self.investt.show()
        self.hide()

    def run(self):
        '''
        Меняет имя пользователя на введенное в диалоговое окно
        :return:
        '''
        name, ok_pressed = QInputDialog.getText(self, " ",
                                                "Введите имя, длинной не более 16 символов")
        if ok_pressed:
            if self.name == name:
                self.statusbar().showMessage(f'Новое имя совпадает с текущим')
            elif len(name) <= 16:
                self.name = name
                self.hello.setText(f'Приветствую, {self.name}!')
                save(self.name, self.score, self.index)
            else:
                self.tip = QMessageBox(self)
                self.tip.setGeometry(300, 300, 200, 100)
                self.tip.setIcon(QMessageBox.Warning)
                self.tip.setWindowTitle('Ошибка')
                self.tip.setText('Имя слишком длинное')
                self.tip.show()

    def add(self):
        '''
        Добавляет на счет сумму, введенную в диалоговом окне
        :return:
        '''
        summ, ok_pressed = QInputDialog.getText(self, "Пополнить счет",
                                                "Добавить на счет:")
        if ok_pressed:
            try:
                self.score += int(summ)
                self.balance.setText(f'На вашем счете: {self.score} @')

                save(self.name, self.score, self.index)
                self.status = True
                update_history(summ, 'Зачисление')
            except ValueError:
                self.tip = QMessageBox(self)
                self.tip.setGeometry(300, 300, 200, 100)
                self.tip.setIcon(QMessageBox.Warning)
                self.tip.setWindowTitle('Ошибка')
                self.tip.setText('Неверный формат данных')
                self.tip.show()


class AboutProject(QWidget):
    '''
    Класс с файлом для души
    '''

    def __init__(self, *args):
        super().__init__()
        uic.loadUi('формы/Помощь.ui', self)
        self.setGeometry(850, 100, 451, 425)
        self.setWindowIcon(QtGui.QIcon('icon.png'))
        with open('help.txt', 'r',
                  encoding='utf-8') as f:
            self.textBrowser.setText(f.read())
        self.setWindowTitle('О проекте')


class Notifications(QWidget):
    '''
    Класс со списком всез уведомлений
    '''

    def __init__(self, *args):
        super().__init__()
        uic.loadUi('формы/Уведомления.ui', self)
        self.setWindowTitle('Уведомления')
        self.setWindowIcon(QtGui.QIcon('icon.png'))
        self.setGeometry(850, 100, 400, 366)
        if len(args[1]) > 0:
            for i in range(len(args[1])):
                if args[1][i][1] != '':
                    self.listWidget.addItem(f'{args[1][i][1]}: На ваш счет '
                                            f'пришли диведенды в размере {args[1][i][0]} @')


class All(QWidget):
    '''
    Класс с диаграммой, отображающей отношение суммы купленных акций к сумме денег на счете
    '''

    def __init__(self, *args):
        super().__init__()
        uic.loadUi('формы/всего в кошельке.ui', self)
        series = QPieSeries()

        plt.pie([args[1][0], args[1][1]], labels=['Наличные', 'Инвестиции'], autopct='%1.2f%%')
        plt.axis("equal")
        plt.get_current_fig_manager().window.setWindowTitle('Статистика')
        plt.get_current_fig_manager().window.setGeometry(850, 100, 496, 400)
        plt.show()


class Diary(QWidget):
    '''
    Класс с задачником для записи целей пользователя
    '''

    def __init__(self, *args):
        super().__init__()
        args = args
        self.setWindowTitle('Задачник')
        self.setGeometry(100, 100, 399, 469)
        self.setWindowIcon(QtGui.QIcon('icon.png'))
        uic.loadUi('формы/Задачник.ui', self)
        self.setWindowTitle('Задачник')
        self.update_points()
        self.add_point.clicked.connect(self.create_point)
        self.up.clicked.connect(self.update_points)
        self.delete_point.clicked.connect(self.delete_)

    def update_points(self):
        '''
        Обновляет таблицу текущих задач
        :return:
        '''
        self.tableWidget.setRowCount(0)
        labels = ['Цель', 'Интервал', 'Каждое\nпополнение']

        self.tableWidget.setColumnCount(3)
        self.tableWidget.setHorizontalHeaderLabels(labels)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        with sqlite3.connect('Points.db') as connect:
            for point, interval, single_pay in connect.execute("SELECT point, interval, single_pay "
                                                               "FROM points WHERE point != ''"):
                row = self.tableWidget.rowCount()
                self.tableWidget.setRowCount(row + 1)

                self.tableWidget.setItem(row, 0, QTableWidgetItem(str(point)))
                self.tableWidget.setItem(row, 1, QTableWidgetItem(str(interval)))
                self.tableWidget.setItem(row, 2, QTableWidgetItem(str(single_pay)))

    def delete_(self):
        '''
        Удаляет задачу с введеным именем
        :return:
        '''
        point, ok_pressed = QInputDialog.getText(self, "Удалить цель",
                                                 "Введите название цели")
        if ok_pressed:
            try:
                con = sqlite3.connect('Points.db')
                cur = con.cursor()
                que = f"DELETE from points\nWHERE Point = '{point}'"

                result = cur.execute(que).fetchall()

                con.commit()
                con.close()
                self.tip = QMessageBox(self)
                self.tip.setGeometry(300, 300, 200, 100)
                self.tip.setIcon(QMessageBox.Information)
                self.tip.setWindowTitle('Успех')
                self.tip.setText('Операция выполнена успешно')
                self.tip.show()
            except Exception:
                self.tip = QMessageBox(self)
                self.tip.setGeometry(300, 300, 200, 100)
                self.tip.setIcon(QMessageBox.Warning)
                self.tip.setWindowTitle('Ошибка')
                self.tip.setText('Такой цели не существует')
                self.tip.show()

    def closeEvent(self, event):
        ex.show()

    def create_point(self):
        '''
        Открывает класс с формой для добавления новой задачи
        :return:
        '''
        self.new_point = NewPoint(self, 'нет данных')
        self.new_point.show()


class NewPoint(QWidget):
    '''
    Класс отвечающий за добавления новой цели в задачник
    '''

    def __init__(self, *args):
        super().__init__()
        uic.loadUi('формы/Добавление Цели.ui', self)
        args = args
        self.setGeometry(550, 100, 360, 398)
        self.setWindowTitle('Добавление цели')
        self.setWindowIcon(QtGui.QIcon('icon.png'))
        self.calcu.clicked.connect(self.count)
        self.cancel.clicked.connect(self.no)
        self.ad_point.clicked.connect(self.ad)

    def count(self):
        '''
        Подсчитывает ежедневный расход на цель
        :return:
        '''
        try:
            all = self.lineEdit_3.text()
            self.number = self.lineEdit_2.text()
            self.label_4.setText(f'Ежедневный платеж: {all} '
                                 f'/ {self.number} = {round(int(all) / int(self.number))}')
            self.single_pay = round(int(all) / int(self.number))
        except Exception:
            self.tip = QMessageBox(self)
            self.tip.setGeometry(300, 300, 200, 100)
            self.tip.setIcon(QMessageBox.Warning)
            self.tip.setWindowTitle('Ошибка')
            self.tip.setText('Проверьте формат данных')
            self.tip.show()

    def no(self):
        self.close()

    def ad(self):
        '''
        Добавляет задачу в таблицу текущих
        :return:
        '''
        try:
            con = sqlite3.connect('Points.db')
            cur = con.cursor()
            que = f"SELECT Point FROM points"

            result = cur.execute(que).fetchall()
            result = [i[0] for i in result]
            result = [i for i in result if i != None]
            con.commit()
            con.close()
            name = self.lineEdit.text()
            if name in result:
                raise Exception

            if self.label_4.text() != 'Ежедневный платеж:':
                con = sqlite3.connect('Points.db')
                cur = con.cursor()
                que = f"INSERT INTO points(Point, interval, single_pay) " \
                      f"VALUES('{name}', {self.number}, {self.single_pay})"

                result = cur.execute(que).fetchall()

                con.commit()
                con.close()
                self.tip = QMessageBox(self)
                self.tip.setGeometry(300, 300, 200, 100)
                self.tip.setIcon(QMessageBox.Information)
                self.tip.setWindowTitle('Успех')
                self.tip.setText('Операция выполнена успешно')
                self.tip.show()
        except Exception:
            self.error = QMessageBox(self)
            self.error.setGeometry(300, 300, 200, 100)
            self.error.setIcon(QMessageBox.Warning)
            self.error.setWindowTitle('Ошибка')
            self.error.setText('Цель с таким названием уже существует.\nПожалуйста, выберете другое.')
            self.error.show()


class History(QWidget):
    '''
    Класс, отвечающий за историю выполнены операций
    '''

    def __init__(self, *args):
        super().__init__()
        uic.loadUi('формы/История платежей.ui', self)
        self.setWindowTitle('История платежей')
        self.setWindowIcon(QtGui.QIcon('icon.png'))
        labels = ['Событие', 'Сумма', 'Дата', 'Время']

        self.tableWidget.setColumnCount(4)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableWidget.setHorizontalHeaderLabels(labels)
        with sqlite3.connect('history1.db') as connect:
            for Event, summ, data, time in connect.execute("SELECT Event, summ, data, time "
                                                           "FROM history WHERE Event != ''"):
                row = self.tableWidget.rowCount()
                self.tableWidget.setRowCount(row + 1)

                self.tableWidget.setItem(row, 0, QTableWidgetItem(str(Event)))
                self.tableWidget.setItem(row, 1, QTableWidgetItem(str(summ)))
                self.tableWidget.setItem(row, 2, QTableWidgetItem(data))
                self.tableWidget.setItem(row, 3, QTableWidgetItem(time))
        self.clear_history.clicked.connect(self.clear)

    def clear(self):
        '''
        Очищает таблицу операций
        :return:
        '''
        self.tableWidget.setRowCount(0)
        con = sqlite3.connect('history1.db')
        cur = con.cursor()

        que = 'DELETE from history'
        result = cur.execute(que).fetchall()

        con.commit()
        con.close()

    def closeEvent(self, event):
        ex.show()


class Invest(QWidget):
    '''
    Класс, отвечающий за инвестиции
    '''

    def __init__(self, *args):
        super().__init__()
        uic.loadUi('формы/Инвестиции-Магазин.ui', self)
        self.setGeometry(100, 100, 699, 517)
        self.setWindowIcon(QtGui.QIcon('icon.png'))
        self.main_form = args[0]
        self.name = args[1][0]
        self.summ = args[1][1]
        self.index = args[1][2]
        self.setWindowTitle('Инвестиции')

        labels = ['Наименование', 'Цена', 'Тип']

        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(labels)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        with sqlite3.connect('Stocks.db') as connect:
            for name, price, type in connect.execute("SELECT name, price, type "
                                                     "FROM stockes WHERE name != ''"):
                row = self.table.rowCount()
                self.table.setRowCount(row + 1)

                self.table.setItem(row, 0, QTableWidgetItem(str(name)))
                self.table.setItem(row, 1, QTableWidgetItem(str(price)))
                self.table.setItem(row, 2, QTableWidgetItem(str(type)))
        self.buy.clicked.connect(self.spend)
        self.my_profile.clicked.connect(self.opened)

    def closeEvent(self, event):
        ex.show()
        plt.close()

    def spend(self):
        '''
        Открывает форму для покупки акций
        :return:
        '''
        self.shop = Shop(self, [self.summ, self.index, self.name])
        self.shop.show()

    def opened(self):
        '''
        Открывает форму с диаграммой купленных акций
        :return:
        '''
        with open('file.txt', mode='r', encoding='utf-8') as f:
            vals = f.readline().rstrip('\n').split(';')
            values = f.readline().rstrip('\n').split(';')
            vals = [float(i) for i in vals]
        self.profile = InvestProfile(self, [vals, values, self.name])
        self.profile.show()


class Shop(QWidget):
    '''
    Класс отвечет за форму для покупки акций
    '''

    def __init__(self, *args):
        super().__init__()
        self.form = args[0].main_form
        self.summ = args[1][0]
        self.index = args[1][1]
        self.name = args[1][2]
        self.lst = {}
        with open('file.txt', mode='r', encoding='utf-8') as f:
            str1 = f.readline().rstrip('\n').split(';')
            str2 = f.readline().rstrip('\n').split(';')
            if str1 != [''] and str2 != ['']:
                for i in range(len(str1)):
                    self.lst[str2[i]] = float(str1[i])

        self.setGeometry(850, 100, 400, 442)
        uic.loadUi('формы/Форма для покупки.ui', self)
        self.setWindowIcon(QtGui.QIcon('icon.png'))
        self.setWindowTitle('Покупка')
        self.calc.clicked.connect(self.calcul)
        self.cancel.clicked.connect(self.cancell)
        self.buy.clicked.connect(self.buyy)
        self.number.setMinimum(1)

        con = sqlite3.connect('Stocks.db')
        cur = con.cursor()
        result = cur.execute("""SELECT name FROM stockes""").fetchall()
        result = [i[0] for i in result]
        result = [i for i in result if i != None]
        self.naim = result[0]
        self.comboBox.addItems(result)
        self.comboBox.activated[str].connect(self.onActivated)

    def onActivated(self, text):
        self.naim = text

    def buyy(self):
        '''
        Функция добавляет купленные акции на счет, обновляет историю платежей, обновляет счет, меняет профиль
        :return:
        '''
        if self.all.text().rstrip(' ') != 'Итого:':
            if self.result <= float(self.summ):
                update_history(self.result, 'Покупка акций')
                self.form.balance.setText(f'На вашем счете: {self.summ - self.result} @')
                save(self.name, self.summ - self.result, self.index)
                if self.namee not in self.lst.keys():
                    self.lst[self.namee] = self.result
                else:
                    self.lst[self.namee] += self.result
                with open('file.txt', mode='w', encoding='utf-8') as g:
                    g.write(';'.join([str(i) for i in self.lst.values()]))
                    g.write('\n')
                    g.write(';'.join(self.lst.keys()))
                self.hide()
                self.error1 = QMessageBox(self)
                self.error1.setGeometry(300, 300, 200, 100)
                self.error1.setIcon(QMessageBox.Information)
                self.error1.setWindowTitle('Успех')
                self.error1.setText('Опперация прошла успешно')
                self.error1.show()
            else:
                self.error1 = QMessageBox(self)
                self.error1.setGeometry(300, 300, 200, 100)
                self.error1.setIcon(QMessageBox.Warning)
                self.error1.setWindowTitle('Ошибка')
                self.error1.setText('На вашем счете недостаточно средств')
                self.error1.show()

    def calcul(self):
        '''
        Рассчитывает итоговую стоимость выбранного количества акций
        :return:
        '''
        # try:
        number = self.number.value()
        con = sqlite3.connect('Stocks.db')
        if number == 0:
            raise Exception

        cur = con.cursor()

        result = cur.execute("""SELECT price FROM stockes
                                WHERE name = ?""", (self.naim,)).fetchall()
        self.all.setText(f'Итого: '
                         f'{str(result[0][0])} * {number} = {round(result[0][0] * int(number), 2)} @')
        self.result = round(result[0][0] * int(number), 2)
        self.namee = self.naim
        # except IndexError:
        #     self.error = QMessageBox(self)
        #     self.error.setGeometry(300, 300, 200, 100)
        #     self.error.setIcon(QMessageBox.Warning)
        #     self.error.setWindowTitle('Ошибка')
        #     self.error.setText('Введенного названия не существует.\nПожалуйста, проверьте данные')
        #     self.error.show()
        # except Exception:
        #     self.error = QMessageBox(self)
        #     self.error.setGeometry(300, 300, 200, 100)
        #     self.error.setIcon(QMessageBox.Warning)
        #     self.error.setWindowTitle('Ошибка')
        #     self.error.setText('Нельзя купить нулевое количесвто акций')
        #     self.error.show()

    def cancell(self):
        self.close()


class InvestProfile(QWidget):
    '''
    Класс отвечает за инвестиционный профиль с диаграммой купленный акций
    '''

    def __init__(self, *args):
        super().__init__()
        uic.loadUi('формы/Инвестиции-Профиль.ui', self)
        self.setWindowTitle('Профиль')
        self.setWindowIcon(QtGui.QIcon('icon.png'))
        self.inv = args[0]
        self.label.setText(f'{args[1][2]},')
        self.all_invest = sum(args[1][0])
        self.label_2.setText(f'за все время вами инвестировано: {str(self.all_invest)}')
        self.setGeometry(850, 100, 496, 150)
        vals = args[1][0]
        labels = args[1][1]
        # self.create_pie(vals, labels)
        plt.pie(vals, labels=labels)
        plt.axis("equal")
        plt.get_current_fig_manager().window.setWindowTitle('Статистика')
        plt.get_current_fig_manager().window.setGeometry(850, 300, 496, 400)
        plt.show()

    def closeEvent(self, event):
        plt.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec())
