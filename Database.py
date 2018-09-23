import sqlite3
import datetime
import os
import logging
from shutil import copyfile


class Student:
    def __init__(self, db_row=None):
        if db_row is None:
            self.found = False
        else:
            self.found = True
            self.id = db_row['id']
            self.first_name = db_row['first_name']
            self.last_name = db_row['last_name']
            self.classgroup = db_row['classgroup']
            self.badgecode = db_row['badgecode']
            self.studentnumber = db_row['studentnumber']
            self.time_ran = db_row['time_ran']
            self.starttime = db_row['starttime']

class RR_DB :
    def __init__(self, log_handle):
        self.cnx = sqlite3.connect(self.DB_DEST, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        self.cnx.row_factory = sqlite3.Row
        self.csr = self.cnx.cursor()
        self.log = logging.getLogger('{}.Database'.format(log_handle))

        #create tables, if they do not exist yet
        for name, ddl in self.TABLES.items():
            self.log.info("Creating table {}: ".format(name))
            self.csr.execute(ddl)

        #make e backup
        self.backup_database()

    DB_FILE = 'rr.db'
    DB_LOCATION = 'resources'
    DB_DEST = os.path.join(DB_LOCATION, DB_FILE)
    DB_BACKUP_LOCATION = os.path.join(DB_LOCATION, 'backup')

    TABLES = {}
    TABLES['students'] = (
        "CREATE TABLE IF NOT EXISTS students ("
        "  id INTEGER PRIMARY KEY UNIQUE NOT NULL,"
        "  badgecode TEXT UNIQUE NOT NULL,"
        "  studentnumber INTEGER, "
        "  first_name TEXT,"
        "  last_name TEXT,"
        "  classgroup TEXT,"
        "  time_ran INTEGER,"
        "  starttime timestamp "
        ")")

    ADD_STUDENT = ("INSERT INTO students "
                 "(last_name, first_name, classgroup, studentnumber, badgecode)"
                 "VALUES (?, ?, ?, ?, ?)")

    UPDATE_GUEST = ("UPDATE students SET "
                    "time_ran=?,"
                    "starttime=?,"
                    "WHERE id=?;")

    #student_list.append((l['NAAM'], l['VOORNAAM'], l['KLAS'], l['LEERLINGNUMMER'], l['RFID']))
    def add_students(self, student_list):
        rslt = True
        try:
            for s in student_list:
                try:
                    self.csr.execute(self.ADD_STUDENT, (s[0], s[1], s[2], s[3], s[4]))
                except sqlite3.Error as e:
                    self.log.error('Could not add to database : {} {} from {}'.format(s[0], s[1], s[2]))
        except sqlite3.Error as e:
            rslt = False
        self.cnx.commit()
        self.log.info('Added students to database')
        return rslt

    def find_student_from_badge(self, badgecode):
        badgecode = badgecode.upper()
        self.csr.execute('SELECT * FROM students WHERE badgecode=?', (badgecode,))
        r = self.csr.fetchone()
        return Student(r)

    def find_student_from_number(self, studentnumber):
        self.csr.execute('SELECT * FROM students WHERE studentnumber=?', (studentnumber,))
        r = self.csr.fetchone()
        return Student(r)

    def find_student_from_id(self, id):
        self.csr.execute('SELECT * FROM students WHERE id=?', (id,))
        r = self.csr.fetchone()
        return Student(r)

    #return a list of student ids
    def get_students_id(self):
        self.csr.execute('SELECT * FROM students')
        rows = self.csr.fetchall()
        students_id = []
        for r in rows:
            students_id.append(r['id'])
        return students_id

    #return all students
    def get_students_sorted_on_time_ran(self):
        self.csr.execute('SELECT * FROM students ORDER BY time_ran ASC, classgroup ASC, last_name ASC, first_name ASC')
        return self.csr.fetchall()

    def update_student(self, id, time_ran, starttime):
        try:
            self.csr.execute('UPDATE students SET time_ran=?, starttime=? WHERE id=?;', (time_ran, starttime, id))
            self.cnx.commit()
            self.log.info('Update student {} {} {}'.format(id, time_ran, starttime))
        except sqlite3.Error as e:
            self.log.error('Could not update student {} {} {}'.format(id, time_ran, starttime))

    def clear_database(self):
        try:
            self.csr.execute('DELETE FROM students;')
            self.cnx.commit()
        except sqlite3.Error as e:
            self.log.error('Could clear database : {}'.format(e))

    def close(self):
        self.cnx.close()

    def backup_database(self):
        try:
            absolute_backup_path = os.path.join(os.getcwd(), self.DB_BACKUP_LOCATION)
            if not os.path.isdir(absolute_backup_path):
                os.mkdir(absolute_backup_path)
            backup_dest = os.path.join(self.DB_BACKUP_LOCATION, datetime.datetime.now().strftime('%Y%m%d%H%M%S') + ' ' + self.DB_FILE )
            copyfile(self.DB_DEST, backup_dest)
        except:
            self.log.info("Could not backup database")
