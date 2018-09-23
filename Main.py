import tkinter as tk
import time, os
from datetime import datetime, date, timedelta
from Database import RR_DB
from Menu import Menu
import locale, random
import logging, logging.handlers


VERSION = 'V1.0'

LOG_FILENAME = 'log/rr-log.txt'
LOG_HANDLE = 'RR'

class RegisterRunner:
    def __init__(self, root=None, log=None):

        self.log = log
        self.LIST_LBX_FORMAT = '{0:<6}{1:<69}{2:<10}{3:<15}'
        self.LIST_LBX_HEIGHT = 20
        self.running_state = False

        #initialize database
        self.database = RR_DB(LOG_HANDLE)

        self.get_students_id()
        random.seed()

        #initialize register
        #self.register = Register(root, self.database, LOG_HANDLE)
        self.menu = Menu(self, root, self.database, LOG_HANDLE)

        #initialize GUI
        self.root=root
        self.root_frm = tk.Frame(self.root)
        self.root_frm.grid()
        self.init_menu()
        self.init_widgets()

        self.actions_on_state()

        #set the minimum size of the window
        root.update()
        root.minsize(root.winfo_width(), root.winfo_height())

    def badge_scanned(self, event):
        #test mode : if 0 is entered, pick a random student from the database
        if self.badge_ent.get() == '0':
            student = self.database.find_student_from_id(random.choice(self.student_id_list))
        else:
            try:
                nbr = int(self.badge_ent.get())
                # 100.000 : arbitrary large number.  If the scanned number is smaller, it is considered a studentnumber
                # else a badgecode (rfid)
                if nbr < 100000:
                    student = self.database.find_student_from_number(nbr)
                else:
                    student = self.database.find_student_from_badge(self.badge_ent.get())
            except:
                student = self.database.find_student_from_badge(self.badge_ent.get())
        self.badge_ent.delete(0, tk.END)
        if student.found:
            d = datetime.now() - self.starttime
            time_ran = d.seconds * 1000 + int(d.microseconds/1000)
            t_min = int(d.seconds/60)
            t_sec = d.seconds - t_min * 60
            t_ms = int(d.microseconds/1000)
            time_str = '{:02d}:{:02d}:{:03d}'.format(t_min, t_sec, t_ms)
            self.database.update_student(student.id, time_ran, self.starttime)
            self.log.info("{} {} {} {}".format(self.list_lbx_idx+1, student.first_name, student.last_name, student.classgroup))
            l = self.LIST_LBX_FORMAT.format(self.list_lbx_idx+1, student.last_name + ' ' + student.first_name, student.classgroup, time_str)
            self.list_lbx.insert('end', l)
            if self.list_lbx_idx % 2 == 0:
                self.list_lbx.itemconfig(self.list_lbx_idx, bg='lightgrey')
            if self.list_lbx_idx >= self.LIST_LBX_HEIGHT:
                self.list_lbx.yview_scroll(1, "units")
            self.list_lbx_idx += 1
        else:
            self.log.error('code {} not found'.format(self.badge_ent.get()))

    def update_time(self):
        #self.time_lbl.configure(text=time.strftime('%M:%S'))
        if self.running_state:
            #print("> " + str(datetime.now()))
            d = datetime.now() - self.starttime
            m = int(d.seconds/60)
            s = d.seconds - 60 * m
            self.time_lbl.configure(text='{:02d}:{:02d}'.format(m, s))
        root.after(1000, self.update_time)

    def clear_display(self):
        self.list_lbx_idx = 0
        self.time_lbl.configure(text='00:00')
        self.list_lbx.delete(0, 'end')

    def get_students_id(self):
        self.student_id_list = self.database.get_students_id()

    #state == true : clock is running
    def actions_on_state(self):
        if self.running_state:
            self.starttime = datetime.now()
            #print("S " + str(self.starttime))
            self.start_stop_btn.config(bg='red', text='Stop')
            self.clear_display()
            self.update_time()
        else:
            self.start_stop_btn.config(bg='green', text='Start')

    def start_stop(self):
        self.running_state = not self.running_state
        self.actions_on_state()

    def init_menu(self):
        #menu
        self.main_mnu = tk.Menu()
        self.menu_mnu=tk.Menu()
        self.main_mnu.add_cascade(label="Menu", menu=self.menu_mnu)
        self.menu_mnu.add_command(label="Import", command=self.menu.import_students)
        self.menu_mnu.add_command(label="Export", command=self.menu.export_results)
        self.menu_mnu.add_separator()
        self.menu_mnu.add_command(label="Wis tijden", command=self.menu.clear_timings)
        self.menu_mnu.add_command(label="Wis database", command=self.menu.clear_database)

        self.root.configure(menu=self.main_mnu)

    def init_widgets(self):
        #Row 0
        self.start_stop_btn = tk.Button(self.root, text="Start", font=("Times New Roman", 40), bd=10, \
                                        activebackground='red', activeforeground='green', command=self.start_stop)
        self.start_stop_btn.grid(row=0, column=0, sticky='w')

        #Row 0 and 1
        self.time_lbl = tk.Label(self.root, text='00:00', font=("Times New Roman", 120))
        self.time_lbl.grid(row=0, column=1, rowspan=2)
        #self.update_time()

        #Row 1
        self.badge_ent = tk.Entry(self.root, font=("Times New Roman", 20))
        self.badge_ent.grid(row=1, column=0, sticky='w')
        self.badge_ent.bind('<Return>', self.badge_scanned)

        #Row 2
        tk.Label(self.root, text=self.LIST_LBX_FORMAT.format('Plts', 'Naam', 'Klas', 'Tijd'), font=('Courier', 15)). \
                grid(row=2, column=0, columnspan=2)
        #ROW 3
        self.list_lbx = tk.Listbox(self.root, height=self.LIST_LBX_HEIGHT, width=100, font=('Courier', 15))
        self.list_lbx.grid(row=3, column=0, rowspan=self.LIST_LBX_HEIGHT, columnspan=2)
        sb1_sb = tk.Scrollbar(self.root)
        sb1_sb.grid(row=3, column=3, rowspan=self.LIST_LBX_HEIGHT)
        self.list_lbx.config(yscrollcommand=sb1_sb.set)
        sb1_sb.config(command=self.list_lbx.yview)
        self.badge_ent.focus_force()


if __name__ == "__main__":
    locale.setlocale(locale.LC_ALL, '')
    root = tk.Tk()
    root.iconbitmap(os.path.join(os.getcwd(), 'resources//fgr.ico'))

    # Set up a specific logger with our desired output level
    log = logging.getLogger(LOG_HANDLE)
    log.setLevel(logging.DEBUG)

    # Add the log message handler to the logger
    log_handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=10 * 1024, backupCount=5)
    log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log_handler.setFormatter(log_formatter)
    log.addHandler(log_handler)

    log.info('start FGR')

    rr = RegisterRunner(root, log)
    root.mainloop()
