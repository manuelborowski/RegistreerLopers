import sqlite3
import datetime
import os
import logging
from shutil import copyfile


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
        "  badge_code TEXT UNIQUE NOT NULL,"
        "  student_number INTEGER, "
        "  first_name TEXT,"
        "  last_name TEXT,"
        "  classgroup TEXT,"
        "  time INTEGER "
        ")")

    ADD_STUDENT = ("INSERT INTO students "
                 "(last_name, first_name, classgroup, student_number, badge_code)"
                 "VALUES (?, ?, ?, ?, ?)")

    UPDATE_GUEST = ("UPDATE students SET "
                    "badge_code=?,"
                    "student_number=?,"
                    "first_name=?,"
                    "last_name=?,"
                    "time=?"
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



    # def find_(self, id):
    #     self.csr.execute('SELECT * FROM guests WHERE id=?', (id,))
    #     r = self.csr.fetchone()
    #     return Guest(r)
    #
    # def find_guest_from_badge(self, badge_code):
    #     self.csr.execute('SELECT * FROM guests WHERE badge_code=?', (badge_code,))
    #     r = self.csr.fetchone()
    #     return Guest(r)
    #
    # def get_guests(self):
    #     self.csr.execute('SELECT * FROM guests ORDER BY last_name, first_name')
    #     r = self.csr.fetchall()
    #     l = []
    #     for i in r:
    #         l.append(Guest(i))
    #     return l
    #
    # def find_guests_from_keywords(self, guest):
    #     qs = 'SELECT * FROM guests WHERE '
    #     added = False
    #     if guest.first_name:
    #         qs += 'first_name LIKE \'%{}%\''.format(guest.first_name)
    #         added = True
    #     if guest.last_name:
    #         if added:
    #             qs += ' AND '
    #         qs += 'last_name LIKE \'%{}%\''.format(guest.last_name)
    #         added = True
    #
    #     if guest.email:
    #         if added:
    #             qs += ' AND '
    #         qs += 'email LIKE \'%{}%\''.format(guest.email)
    #         added = True
    #
    #     if guest.phone:
    #         if added:
    #             qs += ' AND '
    #         qs += 'phone LIKE \'%{}%\''.format(guest.phone)
    #         added = True
    #
    #     if guest.badge_code:
    #         if added:
    #             qs += ' AND '
    #         qs += 'badge_code LIKE \'%{}%\''.format(guest.badge_code)
    #         added = True
    #
    #     if guest.badge_number:
    #         if added:
    #             qs += ' AND '
    #         qs += 'badge_number LIKE \'%{}%\''.format(guest.badge_number)
    #         added = True
    #
    #     self.log.info(qs)
    #     self.csr.execute(qs)
    #     l = []
    #     r = self.csr.fetchall()
    #     for i in r:
    #         l.append(Guest(i))
    #     return l
    #
    #
    # def add_guest(self, badge_code, badge_number, first_name, last_name, email, phone, sub_type, subed_from, payg_left, payg_max):
    #     rslt = True
    #     try:
    #         self.csr.execute(self.ADD_GUEST, (badge_code, badge_number, first_name, last_name, email, phone, sub_type, subed_from, payg_left, payg_max))
    #     except sqlite3.Error as e:
    #         rslt = False
    #     self.cnx.commit()
    #     self.log.info("Guest added : {}, {}, {}, {}, {}, {}".format(first_name, last_name, email, phone, badge_number, sub_type))
    #     return rslt
    #
    #
    # def delete_guest(self, id):
    #     rslt = True
    #     try:
    #         self.csr.execute('DELETE FROM guests WHERE id=?',(id, ))
    #     except sqlite3.Error as e:
    #         rslt = False
    #     self.cnx.commit()
    #     return rslt
    #
    #
    # def update_guest(self, id, badge_code, badge_number, first_name, last_name, email, phone, sub_type, subed_from, payg_left, payg_max):
    #     rslt = True
    #     try:
    #         self.csr.execute(self.UPDATE_GUEST, (badge_code, badge_number, first_name, last_name, email, phone, sub_type, subed_from, payg_left, payg_max, id))
    #     except:
    #         rslt = False
    #     self.cnx.commit()
    #     return rslt
    #
    # def check_registration_time_format(self, time_string):
    #     try:
    #         dt = datetime.datetime.strptime(time_string, '%Y-%m-%d %H:%M:%S')
    #         return True
    #     except Exception as e:
    #         return False
    #
    # def add_registration(self, guest_id, time_in, time_out=None):
    #     rslt = True
    #     try:
    #         # time_in.replace(microsecond=0)
    #         # if time_out:
    #         #     time_out.replace(microsecond=0)
    #         self.csr.execute(self.ADD_REGISTRATION, (time_in, time_out, guest_id))
    #     except Exception as e:
    #         rslt = False
    #     self.cnx.commit()
    #     self.log.info("Registration added : {}, {}".format(guest_id, time_in))
    #     return rslt
    #
    # def update_registration(self, id, guest_id, time_in, time_out):
    #     rslt = True
    #     try:
    #         self.csr.execute(self.UPDATE_REGISTRATION, (time_in, time_out, guest_id, id))
    #     except:
    #         rslt = False
    #     self.cnx.commit()
    #     return rslt
    #
    # def find_last_registration_from_guest(self, guest_id):
    #     l = self.find_registrations_from_guest(guest_id)
    #     if l:
    #         r = l[0] #newest registration
    #     else:
    #         r = Registration()
    #     return r
    #
    #
    # def find_registrations_from_guest(self, guest_id):
    #     self.csr.execute('select * FROM registrations WHERE guest_id=? ORDER BY time_in DESC', (guest_id,))
    #     db_lst = self.csr.fetchall()
    #     lst = []
    #     for i in db_lst:
    #         lst.append(Registration(i))
    #     return lst
    #
    #
    # def find_registration(self, id):
    #     self.csr.execute('SELECT * FROM registrations WHERE id=?', (id,))
    #     r = self.csr.fetchone()
    #     return  Registration(r)
    #
    #
    # def get_registrations_and_guests(self, return_db_rows=False):
    #     raw_select = self.csr.execute('SELECT * FROM registrations JOIN guests ON registrations.guest_id = guests.id ORDER BY time_in DESC')
    #     if return_db_rows: return raw_select
    #     db_lst = self.csr.fetchall()
    #     lst = []
    #     for i in db_lst:
    #         lst.append(Registration(i))
    #     return lst
    #
    #
    # def delete_registration(self, id):
    #     rslt = True
    #     try:
    #         self.csr.execute('DELETE FROM registrations WHERE id=?',(id, ))
    #     except sqlite3.Error as e:
    #         rslt = False
    #     self.cnx.commit()
    #     return rslt


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
