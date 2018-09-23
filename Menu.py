from tkinter import filedialog
from tkinter import messagebox
import os, csv, logging
from datetime import datetime
from xlsxlite.writer import XLSXBook

class Menu:
    def __init__(self, main, root_window, database, log_handle):
        self.root_window = root_window
        self.database = database
        self.main = main
        self.log = logging.getLogger('{}.Register'.format(log_handle))

    def import_students(self):
        options = {}
        options['defaultextension'] = '.csv'
        options['filetypes'] = [('CSV file', '.csv')]
        options['initialdir'] = os.path.expanduser("~") + "/Documents/"
        options['title'] = 'Open een CSV met studenten'
        filename = filedialog.askopenfilename(**options)
        print(filename)

        nbr_students = 0
        try:
            with open(filename, newline='') as csv_file:
                csv_reader = csv.DictReader(csv_file , delimiter=';')
                student_list = []
                for l in csv_reader:
                    #print(l['NAAM'], l['RFID'])
                    student_list.append((l['NAAM'], l['VOORNAAM'], l['KLAS'], l['LEERLINGNUMMER'], l['RFID']))
                    nbr_students += 1

                self.log.info('Import CSV, loaded {} students'.format(nbr_students))
                self.database.add_students(student_list)
                self.main.get_students_id()
                messagebox.showinfo('Import leerlingen', 'Er zijn {} leerlingen geïmporteerd'.format(nbr_students))
        except Exception as e:
            messagebox.showinfo('Import leerlingen', 'Er is iets fout gegaan {}'.format(e))
            self.log.error('Could not import CSV: {}'.format(e))

    def export_results(self):
        now = datetime.now().strftime('%Y%m%d%H%M%S')
        options = {}
        options['defaultextension'] = '.xlsx'
        options['filetypes'] = [('XLSX file', '.xlsx')]
        options['initialdir'] = os.path.expanduser("~") + "/Downloads/"
        options['initialfile'] = 'RegistreerLopers'
        options['title'] = 'Bewaar database in Excel bestand'
        filename = filedialog.asksaveasfilename(**options)
        self.log.info('exporteer naar : {}'.format(filename))
        try:
            f = open(filename, 'w', newline="")
            data = self.database.get_students_sorted_on_time_ran()
            book = XLSXBook()
            sheet = book.add_sheet('uitslag')
            sheet.append_row('NAAM', 'VOORNAAM', 'KLAS', 'TIJD', 'STARTTIJD')
            for r in data:
                if r['time_ran']:
                   time_ran = r['time_ran']
                   starttime = r['starttime']
                else:
                    time_ran = starttime = 0
                t_min = int(time_ran / 60000)
                t_sec = int((time_ran - 60000 * t_min)/ 1000)
                t_msec = time_ran - 60000 * t_min - 1000 * t_sec
                sheet.append_row(r['last_name'], r['first_name'], r['classgroup'], \
                                 '{:02d}:{:02d}.{:03d}'.format(t_min, t_sec, t_msec), starttime)
            book.finalize(to_file=filename)
            messagebox.showinfo('Export', 'Tijden zijn geëxporteerd')
            self.log.info('Resultes are exported')
        except Exception as e:
            messagebox.showinfo('Export', 'Kon niet exporteren : {}'.format(e))
            self.log.error('Could not export : {}'.format(e))

    def clear_database(self):
        r = messagebox.askyesno('Wis de database', 'Bent u zeker dat u al de database wil wissen?', icon='warning')
        if r:
            self.log.info('Clear the database')
            self.database.clear_database()
            try:
                messagebox.showinfo('Wis de database', 'De database is gewist')
                self.main.clear_display()
            except Exception as e:
                messagebox.showinfo('Wis de database', 'Er is iets fout gegaan : {}'.format(e))
        else:
            messagebox.showinfo('Wis de database', 'Afgebroken')
            self.log.info('Abort clear database')

    def clear_timings(self):
        r = messagebox.askyesno('Wis de tijden', 'Bent u zeker dat u al de tijden wil wissen?', icon='warning')
        if r:
            self.log.info('Clear all timings')
            sl = self.database.get_students_id()
            try:
                for s in sl:
                    self.database.update_student(s, None, None)
                messagebox.showinfo('Wis de tijden', 'Alle tijden zijn gewist')
                self.main.clear_display()
            except Exception as e:
                messagebox.showinfo('Wis de tijden', 'Er is iets fout gegaan : {}'.format(e))
        else:
            messagebox.showinfo('Wis de tijden', 'Afgebroken')
            self.log.info('Abort clear all timings')

    def switch_a_q(self):
        pass