import tkinter as tk
from tkinter import messagebox
import time, os
from datetime import datetime, date
from Database import RR_DB
from Menu import Menu
import locale
import logging, logging.handlers

VERSION = 'V1.0'

LOG_FILENAME = 'log/rr-log.txt'
LOG_HANDLE = 'RR'

class RegisterRunner:

    def __init__(self, root=None, log=None):

        self.log = log

        #initialize database
        self.database = RR_DB(LOG_HANDLE)
        #{self.database.test_populate_database()

        #initialize register
        #self.register = Register(root, self.database, LOG_HANDLE)
        self.menu = Menu(root, self.database, LOG_HANDLE)

        #initialize GUI
        self.root=root
        self.root_frm = tk.Frame(self.root)
        self.root_frm.grid()
        self.init_menu()
        self.init_widgets()

        #set the minimum size of the window
        root.update()
        root.minsize(root.winfo_width(), root.winfo_height())

    def badge_scanned(self, event):
        pass
        # guest = self.database.find_guest_from_badge(self.badge_ent.get())
        # if guest.found :
        #     direction = self.register.new_registration(guest)
        #     till_string = ''
        #     if direction == 'IN':
        #         if guest.subscription_type == Guest.SUB_TYPE_SUBSCRIPTION:
        #             delta = FGR_DB.add_years(guest.subscribed_from, 1) - date.today()
        #             if delta.days < 0:
        #                 messagebox.showwarning('Abonnement is verlopen',
        #                                        'Opgelet, uw abonnement is verlopen.\nVraag info aan een medewerker')
        #             else:
        #                 till_string = ', abonnement is nog {} dagen geldig'.format(delta.days)
        #         else:
        #             guest.pay_as_you_go_left -= 1
        #             if guest.pay_as_you_go_left < 0:
        #                 messagebox.showwarning('Beurtenkaart is verlopen',
        #                                        'Opgelet, uw beurtenkaart is verlopen.\nVraag info aan een medewerker')
        #             else:
        #                 till_string = ', er zijn nog {} geldige beurten'.format(guest.pay_as_you_go_left)
        #             rslt = self.database.update_guest(guest.id, guest.badge_code,
        #                                               guest.badge_number, guest.first_name,
        #                                               guest.last_name,
        #                                               guest.email, guest.phone,
        #                                               guest.subscription_type,
        #                                               guest.subscribed_from,
        #                                               guest.pay_as_you_go_left, guest.pay_as_you_go_max)
        #     self.show_message("Hallo {}, u heb juist {} gebadged{}".format(guest.first_name, direction, till_string), 4000, 'green')
        # else:
        #     self.show_message("U bent nog niet geregistreerd, gelieve hulp te vragen", 5000, "red")
        # self.badge_ent.delete(0, tk.END)

    def update_time(self):
        self.time_lbl.configure(text=time.strftime('%d/%m/%Y %H:%M:%S'))
        root.after(1000, self.update_time)

    def clear_database(self):
        answer = tk.Message

    def init_menu(self):
        #menu
        self.main_mnu = tk.Menu()
        self.menu_mnu=tk.Menu()
        self.main_mnu.add_cascade(label="Menu", menu=self.menu_mnu)
        self.menu_mnu.add_command(label="Import", command=self.menu.import_students)
        self.menu_mnu.add_command(label="Export", command=self.menu.export_results)
        #self.menu_mnu.add_command(label="Wis", command=self.clear_database)
        self.root.configure(menu=self.main_mnu)

    def child_window_closes(self):
        pass
        #self.change_mode(self.Mode.guest)


    def init_widgets(self):
        self.fr1_frm = tk.Frame(self.root_frm)
        self.fr1_frm.grid(row=0, column=0, sticky='W')

        #tk.Label(self.root_frm, text = "Welkom bij het fablab\nGelieve uw badge aan te bieden", font=("Times New Roman", 60)).grid(row=1, columnspan=3)

        self.time_lbl = tk.Label(self.root_frm, text=time.strftime('%d/%m/%Y %H:%M:%S'), font=("Times New Roman", 60))
        self.time_lbl.grid(row=2, columnspan=3)
        self.update_time()

        tk.Label(self.root_frm, text = "", font=("Times New Roman", 30)).grid(columnspan=3, sticky='E')

        self.fr2_frm = tk.Frame(self.root_frm)
        self.fr2_frm.grid(columnspan=3, sticky='W')
        tk.Label(self.fr2_frm, text = "BADGE", font=("Times New Roman", 30)).pack(side='left')
        self.badge_ent = tk.Entry(self.fr2_frm, show='*', font=("Times New Roman", 30))
        self.badge_ent.pack(side='left')
        self.badge_ent.bind('<Return>', self.badge_scanned)

        self.guest_welcome_lbl = tk.Label(self.root_frm, text ="", font=("Times New Roman", 20))
        self.guest_welcome_lbl.grid(columnspan=3, sticky='W')

        tk.Label(self.root_frm, text = "", font=("Times New Roman", 30)).grid(columnspan=3, sticky='E')


    def show_message(self, msg, time=2000, color='black'):
        def clear_msg():
            self.guest_welcome_lbl.config(text = '')
        #self.root_frm.focus()
        self.guest_welcome_lbl.config(text=msg, fg=color)
        self.root_frm.after(time, clear_msg)


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
