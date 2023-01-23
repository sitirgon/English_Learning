import sqlite3
import os
import time
from datetime import date
from tabulate import tabulate


class ConnectBase:
    def __init__(self):
        self.path_documents = os.path.expanduser('~\Documents\Słownik')
        try:
            os.mkdir(self.path_documents)
        except:
            pass
        self.con = sqlite3.connect(self.path_documents+'\\Dict.db')
        self.cur = self.con.cursor()
        self.cur_update = self.con.cursor()
        try:
            # base config
            self.cur.execute('''CREATE TABLE Words(
                            ID INTEGER PRIMARY KEY,
                            Word VARCHAR(50),
                            RepeatDate DATE,
                            CrashTEST VARCHAR(3),
                            CountRepeatCorrect INTEGER,
                            CreationDate DATE)''')
            self.cur.execute('''CREATE TABLE Definitions(
                            ID INTEGER PRIMARY KEY,
                            IDWords INTEGER,
                            Definition VARCHAR(50))''')
            self.con.commit()
        except sqlite3.OperationalError:
            pass


def add_new_word():
    data_creation = date.fromtimestamp(time.time())
    data_repeat = date.fromtimestamp(time.time() + 86_400)
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
        sql.cur.execute('''INSERT INTO Words (
                word,
                CountRepeatCorrect, 
                CrashTest, 
                RepeatDate, 
                CreationDate)
                VALUES (?,1,'NIE',?,?)''',
                        (word, data_repeat, data_creation))
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
            checkDefinition = sql.cur.execute('''
                                            SELECT 
                                                Definition
                                            FROM 
                                                Words W
                                                LEFT JOIN Definitions D on D.IDWords = W.ID
                                            WHERE 
                                                W.Word = ?
                                                AND D.Definition = ?''',
                                            (word, notEmpty))
            checkDefinition = checkDefinition.fetchall()
            if checkDefinition:
                print('Do odanego słowa definicja jest przypisana')
                continue
            elif notEmpty != '':
                definition.append(notEmpty)
            elif notEmpty == '':
                break
            i += 1
        add_new_definition_loop(word, definition)
        os.system('cls')
        print('Znaczenie dodano pomyślnie')
        os.system('pause')
    elif not wordCheck:
        os.system('cls')
        print('Podane słowo nie istnieje')
        os.system('pause')


def repeat_word():
    sql.cur.execute('''
    UPDATE
    words
    SET 
    COUNTREPEATCORRECT = 1
    WHERE
    REPEATDATE <= DATE('NOW','-2 DAY')
    ''')
    sql.con.commit()
    os.system('cls')
    day = 86_400
    select = sql.cur.execute('''
                            select 
                                w.Word
                                ,count(definition)
                            from 
                                words w
                                left join definitions d on w.id = d.idwords
                            where
                                w.repeatdate <= date()
                            group by
                                w.Word
                            order by 
                                RANDOM()''')
    select = select.fetchall()
    if not select:
        print('Brak słówek do powtórki!')
        os.system('pause')
    elif select:
        print('Słowa do powtórki:', len(select))
        answer = input('Chcesz zacząć powtórke? (tak/nie) ')
        if answer == 'tak':
            for i in select:
                os.system('cls')
                print('Słowo:', i[0])
                definition_word = sql.cur.execute('''
                                                    select 
                                                        d.Definition
                                                        ,w.RepeatDate
                                                        ,w.CountRepeatCorrect
                                                        ,w.Id
                                                    from 
                                                        words w
                                                        left join definitions d on w.id = d.idwords
                                                    where
                                                        W.WORD = ?''', (i[0],))
                definition_word = definition_word.fetchall()
                correct_definitions = 0; try_score = 0
                while correct_definitions < i[1]:
                    try_score += 1
                    correct_answer = False
                    repeat_answer = input('Znaczenie: ')
                    for k in definition_word:
                        if repeat_answer == k[0]:
                            correct_definitions += 1
                            correct_answer = True
                    if correct_answer:
                            continue
                    elif not correct_answer:
                        while True:
                            try_score += 1
                            print('Odpowiedz niepoprawna, spróbuj jeszcze raz')
                            repeat_answer_second = input('Znaczenie: ')
                            for definition_check in definition_word:
                                if repeat_answer_second == definition_check[0]:
                                    correct_definitions += 1
                                    correct_answer = True
                                    continue
                            if correct_answer:
                                break
                if i[1] == try_score:
                    print(f'\nWynik to {i[1]}/{try_score} powtórka {date.fromtimestamp(time.time() + (day * ((k[2])+1)))}')
                    sql.cur.execute('update words set RepeatDate = ?, CountRepeatCorrect = ? where id = ?',
                                            (date.fromtimestamp(time.time() + (day * ((k[2])+1))), k[2] + 1, k[3]))
                    sql.con.commit()
                elif try_score > i[1]:
                    print(f'\nWynik to {i[1]}/{try_score} powtórka {date.fromtimestamp(time.time() + day)}')
                    sql.cur.execute('update words set RepeatDate = ?, CountRepeatCorrect = ? where id = ?',
                                                    (date.fromtimestamp(time.time() + day) , 1, definition_check[3]))
                    sql.con.commit()
                time.sleep(1.5)  
            os.system('cls')
            print('To wszystko')
            os.system('pause')
        elif answer == 'nie':
            return


def crash_test():
    day = 86_400
    select = select_sql()
    if len(select) == 0:
        sql.cur.execute("UPDATE words SET CRASHTEST = 'NIE'")
        sql.con.commit()
    while True:
        os.system('cls')
        answer = input('Chcesz zacząć powtórke? (tak/nie) ')
        if answer == 'tak':
            select = select_sql()
            os.system('cls')
            print('Witaj w CrashTest')
            print(f'CrashTest możesz przeprowadzić na {len(select)}')
            count_of_select = int(input('Wprowadź liczbe słówek: '))
            if count_of_select > len(select):
                print('\nWprowadzono za dużą liczbę!')
                os.system('pause')
                continue
            elif count_of_select <= len(select):
                count = 0
                for i in select:
                    count += 1
                    if count > count_of_select:
                        break
                    os.system('cls')
                    print('Słowo:', i[0])
                    definition_word = sql.cur.execute('''
                                                        select 
                                                            d.Definition
                                                            ,w.Id
                                                        from 
                                                            words w
                                                            left join definitions d on w.id = d.idwords
                                                        where
                                                            W.WORD = ?''', (i[0],))
                    definition_word = definition_word.fetchall()
                    correct_definitions = 0; try_score = 0
                    while correct_definitions < i[4]:
                        try_score += 1
                        correct_answer = False
                        repeat_answer = input('Znaczenie: ')
                        for k in definition_word:
                            if repeat_answer == k[0]:
                                correct_definitions += 1
                                correct_answer = True
                        if correct_answer:
                                continue
                        elif not correct_answer:
                            while True:
                                try_score += 1
                                print('Odpowiedz niepoprawna, spróbuj jeszcze raz')
                                repeat_answer_second = input('Znaczenie: ')
                                for definition_check in definition_word:
                                    if repeat_answer_second == definition_check[0]:
                                        correct_definitions += 1
                                        correct_answer = True
                                        continue
                                if correct_answer:
                                    break
                    if i[4] == try_score:
                        print(f'\nWynik to {i[4]}/{try_score}')
                        sql.cur.execute('update words set CrashTest = ? where id = ?',
                                                ('TAK', k[1]))
                        sql.con.commit()
                    elif try_score > i[4]:
                        print(f'\nWynik to {i[4]}/{try_score}')
                        sql.cur.execute('update words set CrashTest = ? where id = ?',
                                                        ('TAK', k[1]))
                        sql.con.commit()
                    time.sleep(1.5)  
                os.system('cls')
                print('To wszystko')
                os.system('pause')
        elif answer == 'nie':
            break
        break



def view_db():
    os.system('cls')
    print('Przegląd bazy...')
    headers = ['ID', 'Słowo', 'Znaczenie', 'Licznik', 'Data Wpisu', 'Data Powtórki', 'Powtórka']
    a = sql.cur.execute('''
    SELECT
        W.ID,
        W.WORD,
        D.DEFINITION,
        W.COUNTREPEATCORRECT,
        W.CREATIONDATE,
        W.REPEATDATE,
        W.CrashTEST
    FROM
        WORDS W
        LEFT JOIN DEFINITIONS D ON W.ID = D.IDWORDS
    ORDER BY
        WORD
        ''')
    table = a.fetchall()
    print(tabulate(table, headers, tablefmt='github', numalign="center", stralign="center"))
    os.system('pause')


def remove_word():
    os.system('cls')
    print('Usuwanie słowa...')
    removeWord = input('Podaj ID słówka do usunięcia: ')
    os.system('cls')
    print('Trwa usuwanie...')
    sql.cur.execute('DELETE FROM Definitions WHERE IDWords = ?', (removeWord,))
    sql.cur.execute('DELETE FROM Words WHERE ID = ?', (removeWord,))
    sql.con.commit()
    time.sleep(1)
    os.system('cls')
    print('Usuwanie pomyślne')
    os.system('pause')


def add_new_definition_loop(word, definition):
    data_creation = date.fromtimestamp(time.time())
    data_repeat = date.fromtimestamp(time.time() + 86_400)
    idWords = sql.cur.execute('select ID from Words where word = ?', (word,))
    idWords = idWords.fetchall()
    for k in definition:
        sql.cur.execute('''INSERT INTO Definitions (
                IDWords,
                Definition)
                VALUES (?,?)''',
                        (idWords[0][0], k))
        sql.con.commit()


def select_sql():
    select = sql.cur.execute('''
    SELECT
        W.WORD,
        D.DEFINITION,
        W.CRASHTEST,
        W.ID,
        COUNT(definition)
    FROM
        WORDS W
        LEFT JOIN DEFINITIONS D ON W.ID = D.IDWORDS
    WHERE 
        CRASHTEST = 'NIE'
    GROUP BY
        W.WORD
    ORDER BY
        RANDOM()''')
    select = select.fetchall()
    return select


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


