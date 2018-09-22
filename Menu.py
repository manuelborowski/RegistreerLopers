from tkinter import filedialog
import os, csv, logging


class Menu:
    def __init__(self, root_window, database, log_handle):
        self.root_window = root_window
        self.database = database
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
        except Exception as e:
            self.log.error('Could not import CSV: {}'.format(e))

    def export_results(self):
        pass