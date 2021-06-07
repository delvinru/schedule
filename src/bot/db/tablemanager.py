import psycopg2

class Database(object):
    def __init__(self, database, user, password, host, port):
        self.con = psycopg2.connect(
            database=database,
            user=user,
            password=password,
            host=host,
            port=port
        )
        self.cursor = self.con.cursor()

    def _clear_table(self, table):
        '''
        Отчистка таблицы.
        '''
        if table == "SCHEDULE":
            self.cursor.execute('DELETE FROM SCHEDULE *')
        elif table == "EXAMS":
            self.cursor.execute('DELETE FROM EXAMS *')
        self.con.commit()
        print("Successfully cleared table " + table)

    def _delete_table(self, table):
        '''
        Удалить таблицу.
        '''
        if table == "SCHEDULE":
            self.cursor.execute('DROP TABLE SCHEDULE')
        elif table == "EXAMS":
            self.cursor.execute('DROP TABLE EXAMS')
        self.con.commit()
        print("Successfully deleted table " + table)

    def end(self):
        '''
        Закрыть соединение.
        '''
        self.con.commit()
        self.con.close()

    def clear_Schedule(self, table):
        '''
        Отчистить таблицу Schedule.
        '''
        self._clear_table(table)

    def rebuild_Schedule(self, table):
        '''
        Удалить и пересоздать таблицу Schedule
        '''
        self._delete_table(table)
        self.init_table()
    
    def insert_user(self, tgid: int, username: str, first_name: str, lang: str, group: str):
        """ Save user in database """
        query = "INSERT INTO profiles (tgid, username, first_name, language_code, group_name) VALUES (%s, %s, %s, %s, %s)"
        self.cursor.execute(query, (tgid, username, first_name, lang, group, ))
        self.con.commit()
    
    def get_user_group(self, tgid: int) -> str:
        """ Get user from database """

        query = "SELECT group_name FROM profiles WHERE tgid = %s"
        self.cursor.execute(query, (tgid, ))
        data = self.cursor.fetchone()
        if not data:
            return ''
        else:
            return data[0]
    
    def update_user_info(self, tgid: int, group: str):
        """ Update user group in table """

        query = "UPDATE profiles SET group_name=%s WHERE tgid=%s"
        self.cursor.execute(query, (group, tgid, ))
        self.con.commit()
    
    def insert_lesson(self, idn, group, day_now, lesson, typ, audit, start_time, end_time, order, even, strweek):
        query = """
        INSERT INTO SCHEDULE (ID,GRP,DAY,LESSON,TYPE,AUDIT,START_TIME,END_TIME,ORD,EVEN,WEEK)
        VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        self.cursor.execute(query, (idn, group, day_now, lesson, typ, audit, start_time, end_time, order, even, strweek, ))

    def insert_exam(self, idn, group, day, exam, typ, lector, time, audit):
        query = """
        INSERT INTO EXAMS (ID,GRP,DAY,EXAM,TYPE,LECTOR,TIME,AUDIT)
        VALUES(%s,%s,%s,%s,%s,%s,%s,%s)
        """
        self.cursor.execute(query, (idn, group, day, exam, typ, lector, time, audit, ))
    
    def select_group_and_week_day(self, group, week_day, even_week):
        query = """
            SELECT * FROM SCHEDULE
            WHERE grp=%s and day=%s and even=%s
            ORDER BY id;
        """
        self.cursor.execute(query, (group, week_day, even_week, ))
        return self.cursor.fetchall()

    def select_group(self, group):
        query = """
            SELECT * FROM SCHEDULE
            WHERE grp=%s
            ORDER BY id;
        """
        self.cursor.execute(query, (group, ))
        return self.cursor.fetchall()
    
    def select_group_and_even_week(self, group, even_week):
        query = """
        SELECT * FROM SCHEDULE
        WHERE grp=%s and even=%s
        ORDER BY id;
        """
        self.cursor.execute(query, (group, even_week, ))
        return self.cursor.fetchall()

    def select_group_exams(self, group):
        query = """
        SELECT * FROM EXAMS
        WHERE grp=%s
        ORDER BY id;
        """
        self.cursor.execute(query, (group, ))
        return self.cursor.fetchall()
    
    def single_commit(self):
        self.con.commit()