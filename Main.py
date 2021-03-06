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
        self.switch_q_a = True
        self.actions_on_q_a_state()
        self.rfid_reader_M301 = False
        self.actions_on_M301_present()

        #initialize database
        self.database = RR_DB(LOG_HANDLE)

        self.get_students_id()
        random.seed()

        self.menu = Menu(self, root, self.database, LOG_HANDLE)

        #initialize GUI
        self.root=root
        self.root_frm = tk.Frame(self.root)
        self.root_frm.grid()
        self.init_menu()
        self.init_widgets()

        self.actions_on_running_state()

        #set the minimum size of the window
        root.winfo_toplevel().title("Lopers Tijd Registratie {}".format(VERSION))
        root.update()
        root.minsize(root.winfo_width(), root.winfo_height())

    def badge_scanned(self, event):
        if self.running_state:
            #test mode : if 0 is entered, pick a random student from the database
            badgecode = self.badge_ent.get().upper()
            if badgecode == '0':
                student = self.database.find_student_from_id(random.choice(self.student_id_list))
            else:
                try:
                    nbr = int(badgecode)
                    # 100.000 : arbitrary large number.  If the scanned number is smaller, it is considered a studentnumber
                    # else a badgecode (rfid)
                    if nbr < 100000:
                        student = self.database.find_student_from_number(nbr)
                    else:
                        #If the M301 reader is used then the rfid code must be translated to hex and byteswapped
                        if self.rfid_reader_M301:
                            h = '{:0>8}'.format(hex(nbr).split('x')[-1].upper())
                            badgecode = h[6:8] + h[4:6] + h[2:4] + h[0:2]
                        student = self.database.find_student_from_badge(badgecode)
                except:
                    #an RFID code is scanned, with potentianaly a Q in it.  The Q needs to be changed to an A
                    if self.switch_q_a:
                        badgecode = badgecode.replace('Q', 'A')

                    student = self.database.find_student_from_badge(badgecode)
            if student.found:
                d = datetime.now() - self.starttime
                time_ran = d.seconds * 1000 + int(d.microseconds/1000)
                t_min = int(d.seconds/60)
                t_sec = d.seconds - t_min * 60
                t_ms = int(d.microseconds/1000)
                time_str = '{:02d}:{:02d},{:03d}'.format(t_min, t_sec, t_ms)
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
        self.badge_ent.delete(0, tk.END)

    def actions_on_q_a_state(self):
        if self.switch_q_a:
            self.switch_q_a_menu_label = 'WEL Q naar A veranderen'
        else:
            self.switch_q_a_menu_label = 'NIET Q naar A veranderen'

    def switch_a_q_state(self):
        self.switch_q_a = not self.switch_q_a
        self.actions_on_q_a_state()

    def actions_on_M301_present(self):
        if self.rfid_reader_M301:
            self.M301_present_menu_label = 'M301 WORDT gebruikt'
        else:
            self.M301_present_menu_label = 'M301 wordt NIET gebruikt'

    def switch_M301_present_state(self):
        self.rfid_reader_M301 = not self.rfid_reader_M301
        self.actions_on_M301_present()


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
    def actions_on_running_state(self):
        self.starttime = datetime.now()
        if self.running_state:
            #print("S " + str(self.starttime))
            self.start_stop_btn.config(bg='red', text='Stop')
            self.clear_display()
            self.update_time()
        else:
            self.start_stop_btn.config(bg='green', text='Start')

    def start_stop(self):
        self.running_state = not self.running_state
        self.actions_on_running_state()

    def update_menu(self):
        self.menu_mnu.entryconfig(7, label=self.switch_q_a_menu_label)
        self.menu_mnu.entryconfig(8, label=self.M301_present_menu_label)

    def init_menu(self):
        #menu
        self.main_mnu = tk.Menu(postcommand=self.update_menu)
        self.menu_mnu=tk.Menu()
        self.main_mnu.add_cascade(label="Menu", menu=self.menu_mnu)
        self.menu_mnu.add_command(label="Import", command=self.menu.import_students)
        self.menu_mnu.add_command(label="Export", command=self.menu.export_results)
        self.menu_mnu.add_separator()
        self.menu_mnu.add_command(label="Wis tijden", command=self.menu.clear_timings)
        self.menu_mnu.add_command(label="Wis database", command=self.menu.clear_database)
        self.menu_mnu.add_separator()
        self.menu_mnu.add_command(label=self.switch_q_a_menu_label, command=self.switch_a_q_state)
        self.menu_mnu.add_command(label=self.M301_present_menu_label, command=self.switch_M301_present_state)

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
    root.iconbitmap(os.path.join(os.getcwd(), 'resources//rr.ico'))

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
