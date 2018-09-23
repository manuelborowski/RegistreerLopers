from tkinter import filedialog
from tkinter import messagebox
import os, csv, logging


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
        pass

    def clear_database(self):

        pass

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
        pass