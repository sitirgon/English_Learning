import datetime
import sqlite3
import os
import time
from datetime import date


class ConnectBase:
    def __init__(self):
        self.con = sqlite3.connect('Dict.db')
        self.cur = self.con.cursor()
        self.cur_update = self.con.cursor()
        try:
            # base config
            self.cur.execute('''CREATE TABLE Words(
                            ID INTEGER PRIMARY KEY,
                            Word VARCHAR(50),
                            IDWord INTEGER,
                            CountRepeatCorrect INTEGER,
                            CrashTest VARCHAR(3),
                            RepeatDate DATE,
                            CreationDate DATE)''')
            self.cur.execute('''CREATE TABLE Definitions(
                            ID INTEGER PRIMARY KEY,
                            IDWords INTEGER,
                            Definition VARCHAR(50))''')
            self.cur.execute('''CREATE TABLE Context(
                            IDDefinitions INTEGER,
                            Context_Definition VARCHAR(50))''')
            self.con.commit()
        except sqlite3.OperationalError:
            pass


def add_new_word():
    definition = []
    os.system('cls')
    print('Dodaj nowe słowo')
    word = input('Słowo: ')
    checkWord = sql.cur.execute('SELECT Word FROM Words WHERE Word = ?', (word,))
    checkWord = checkWord.fetchall()
    if not checkWord:
        i = 1
        while True:
            notEmpty = input(f'Znaczenie {i}: ')
            if notEmpty != '':
                definition.append(notEmpty)
            elif notEmpty == '':
                break
            i += 1
        os.system('cls')
        print('Dodaje nowe słowo...')
        time.sleep(1)
        data_creation = date.fromtimestamp(time.time())
        data_repeat = date.fromtimestamp(time.time() + 86_400)
        sql.cur.execute(
            '''INSERT INTO Words (
            Word, 
            CountRepeatCorrect, 
            CrashTest, 
            RepeatDate, 
            CreationDate) 
            VALUES (?,1,?,?,?)''',
            (word, 'NIE', data_repeat, data_creation))
        sql.con.commit()
        add_new_definition_loop(word, definition)
        os.system('cls')
        print('Słowo dodano pomyślnie.')
        os.system('pause')
    elif checkWord:
        os.system('cls')
        print('Słowo już zostało dodane, jeżeli chcesz dodać nową definicje tego słowa użyj innej funkcji.')
        os.system('pause')


def add_new_definition():
    definition = []
    os.system('cls')
    print('Dodaj nową definicję do istniejącego słowa')
    word = input('Podaj słowo: ')
    wordCheck = sql.cur.execute('SELECT Word FROM Words WHERE Word = ?', (word,))
    wordCheck = wordCheck.fetchall()
    if wordCheck:
        i = 1
        while True:
            notEmpty = input(f'Znaczenie {i}: ')
            if notEmpty != '':
                definition.append(notEmpty)
            elif notEmpty == '':
                break
            i += 1
        print('Dodawanie znaczeń')
        add_new_definition_loop(word, definition)
        os.system('cls')
        print('Znaczenie dodano pomyślnie')
        os.system('pause')
    elif not wordCheck:
        os.system('cls')
        print('Podane słowo nie istnieje')
        os.system('pause')


def repeat_word():
    os.system('cls')
    day = 86_400
    select = sql.cur.execute('select Word, Definition, CountRepeatCorrect, RepeatDate, id from words order by RANDOM()')
    select = select.fetchall()
    count_word = 0
    for i in select:
        data_repeat = datetime.datetime.strptime(i[3], '%Y-%m-%d').date()
        if data_repeat <= date.fromtimestamp(time.time()):
            count_word += 1
    if count_word == 0:
        print('Brak słówek do powtórki!')
        os.system('pause')
    elif count_word > 0:
        print('Słowa do powtórki:', count_word)
        answer = input('Chcesz zacząć powtórke? (tak/nie) ')
        if answer == 'tak':
            for i in select:
                data_repeat = datetime.datetime.strptime(i[3], '%Y-%m-%d').date()
                if data_repeat <= date.fromtimestamp(time.time()):
                    os.system('cls')
                    print('Słowo:', i[0])
                    repeat_answer = input('In English: ')
                    if repeat_answer == i[1]:
                        print('Odpowiedź poprawna')
                        sql.cur.execute('update words set RepeatDate = ?, CountRepeatCorrect = ? where id = ?',
                                        (date.fromtimestamp(time.time() + (day * (i[2] + 1))), i[2] + 1, i[4]))
                        sql.con.commit()
                        time.sleep(1)
                        continue
                    elif repeat_answer != i[1]:
                        while True:
                            os.system('cls')
                            print('Odpowiedz niepoprawna, spróbuj jeszcze raz')
                            print('Słowo:', i[0])
                            repeat_answer_second = input('In English: ')
                            if repeat_answer_second == i[1]:
                                print('Odpowiedź poprawna')
                                sql.cur.execute('update words set RepeatDate = ?, CountRepeatCorrect = ? where id = ?',
                                                (date.fromtimestamp(time.time() + day) , 1, i[4]))
                                sql.con.commit()
                                time.sleep(1)
                                break
                            elif repeat_answer_second != i[1]:
                                continue
            print('To wszystko')
            os.system('pause')
        elif answer == 'nie':
            return


def crash_test():
    while True:
        os.system('cls')
        select = sql.cur.execute("SELECT word, definition, crashtest, id FROM WORDS WHERE CRASHTEST = 'NIE' ORDER BY RANDOM()")
        select = select.fetchall()
        if len(select) == 0:
            sql.cur.execute("UPDATE WORDS SET CRASHTEST = 'TAK'")
            sql.con.commit()
        print('Witaj w CrashTest')
        print(f'CrashTest możesz przeprowadzić na {len(select)}')
        count_of_select = int(input('Wprowadź liczbe słówek: '))
        if count_of_select > len(select):
            print('\nWprowadzono za dużą liczbę!')
            continue
        elif count_of_select <= len(select):
            for i in select:
                os.system('cls')
                print('Słowo:', i[0])
                answer = input('In English: ')
                if answer == i[1]:
                    print('Odpowiedź poprawna')
                    sql.cur.execute("UPDATE WORDS SET CRASHTEST = 'TAK' WHERE ID = ?", (i[3],))
                    sql.con.commit()
                    time.sleep(1)
                    continue
                elif answer != i[1]:
                    while True:
                        os.system('cls')
                        print('Odpowiedź niepoprwana, spróbuj jeszcze raz')
                        print('Słowo:', i[0])
                        answer_again = input('In English: ')
                        if answer_again == i[1]:
                            print('Odpowiedź poprawna')
                            sql.cur.execute("UPDATE WORDS SET CRASHTEST = 'TAK' WHERE ID = ?", (i[3],))
                            sql.con.commit()
                            time.sleep(1)
                            break
                        elif answer_again != i[1]:
                            continue


def view_db():
    os.system('cls')
    print('Przegląd bazy...')
    up = '# ID ####### Słowo ########## In English ##### Licznik ## Data Wpisu ## Data Powtórki #'
    print(up)
    a = sql.cur.execute('''
    SELECT 
        * 
    FROM 
        Words
        ''')
    for i in a:
        print(f'# {i[0]}  ## {i[1]}'+' '*(15-len(i[1]))+f' ## {i[2]}'+' '*(15-len(i[2]))+f' ## {i[3]}'+' '*(8-len(str(i[3])))+f' ## {i[6]} ## {i[5]}    #')
    print('#'*len(up))
    os.system('pause')


def remove_word():
    os.system('cls')
    print('Usuwanie słowa...')
    removeWord = input('Podaj ID słówka do usunięcia: ')
    os.system('cls')
    print('Trwa usuwanie...')
    sql.cur.execute('DELETE FROM Words WHERE ID = ?', (removeWord,))
    sql.cur.execute('DELETE FROM Definitions WHERE IDWords = ?', (removeWord,))
    sql.con.commit()
    time.sleep(1)
    os.system('cls')
    print('Usuwanie pomyślne')
    os.system('pause')


def add_new_definition_loop(word, definition):
    idWords = sql.cur.execute('select ID from Words where word = ?', (word,))
    idWords = idWords.fetchall()
    for k in definition:
        sql.cur.execute('''INSERT INTO Definitions (
                IDWords,
                Definition)
                VALUES (?,?)''',
                        (idWords[0][0], k))
        sql.con.commit()


def main():
    while True:
        os.system('cls')
        print('''Witam w programie
1.Dodaj nowe słowo
2.Dodaj nowe znaczenie
3.Powtórka słów
4.Crash test
5.Przegląd bazy słówek
6.Usuwanie słówka
0.Wyjście''')

        choose = input('Wybierz opcje: ')

        match choose:
            case '1':
                add_new_word()
            case '2':
                add_new_definition()
            case '3':
                repeat_word()
            case '4':
                crash_test()
            case '5':
                view_db()
            case '6':
                remove_word()
            case '0':
                print('Wyjście...')
                break
            case _:
                print('Wyjście...')
                break


if __name__ == '__main__':
    sql = ConnectBase()
    main()



