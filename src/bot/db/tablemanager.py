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

    def init_table(self):
        # Create table Schedule
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS SCHEDULE  
                (ID INT PRIMARY KEY NOT NULL,
                GRP TEXT,
                DAY TEXT,
                LESSON TEXT,
                TYPE TEXT,
                AUDIT TEXT,
                ORD INT,
                EVEN TEXT,
                WEEK INT[]
            );
        """) 
        self.con.commit()
        # Create table for user profiles
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS profiles
            (ID SERIAL PRIMARY KEY,
            tgid BIGINT UNIQUE NOT NULL,
            username VARCHAR(64) NOT NULL,
            first_name VARCHAR(64) NOT NULL,
            language_code VARCHAR(8) NOT NULL,
            group_name VARCHAR(64) NOT NULL
            );
            """
        )
        self.con.commit()
        print("Successfully created table Schedule")

    def _clear_table(self):
        '''
        Отчистка таблицы.
        '''
        self.cursor.execute('DELETE FROM SCHEDULE *')
        self.con.commit()
        print("Successfully cleared table Schedule")

    def _delete_table(self):
        '''
        Удалить таблицу.
        '''
        self.cursor.execute('DROP TABLE SCHEDULE')
        self.con.commit()
        print("Successfully deleted table Schedule")

    def end(self):
        '''
        Закрыть соединение.
        '''
        self.con.commit()
        self.con.close()

    def clear_Schedule(self):
        '''
        Отчистить таблицу Schedule.
        '''
        self._clear_table()

    def rebuild_Schedule(self):
        '''
        Удалить и пересоздать таблицу Schedule
        '''
        self._delete_table()
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
        print(data)
        if not data:
            return ''
        else:
            return data[0]
    
    def insert_lesson(self, idn, group, day_now, lesson, typ, audit, order, even, strweek):
        query = """
        INSERT INTO SCHEDULE (ID,GRP,DAY,LESSON,TYPE,AUDIT,ORD,EVEN,WEEK)
        VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        self.cursor.execute(query, (idn, group, day_now, lesson, typ, audit, order, even, strweek, ))
    
    def select_group_and_week_day(self, group, week_day, even_week):
        query = """
            SELECT * FROM SCHEDULE
            WHERE grp=%s and day=%s and even=%s
            ORDER BY id;
        """
        self.cursor.execute(query, (group, week_day, even_week, ))
        return self.cursor.fetchall()
    
    def select_group_and_even_week(self, group, even_week):
        query = """
        SELECT * FROM SCHEDULE
        WHERE grp=%s and even=%s
        ORDER BY id;
        """
        self.cursor.execute(query, (group, even_week, ))
        return self.cursor.fetchall()
    
    def single_commit(self):
        self.con.commit()