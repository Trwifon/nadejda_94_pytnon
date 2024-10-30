import tkinter
import psycopg2
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import tkinter.font as tkFont

empty_dictionary = {
    'date': datetime.now().date(),
    'warehouse': 'P',
    'partner_name': '',
    'partner_id': 0,
    'partner_type': '',
    'open_balance': 0,
    'order_type': '',
    'amount': 0,
    'close_balance': 0,
    'note': '',
    'order': ''
}
main_dictionary = empty_dictionary.copy()

dict_connection = {
    'host': '127.0.0.1',
    # 'host': '192.168.5.16',
    'port': '5432',
    'user': 'postgres',
    'password': 'Jabbour123+',
    'database': 'nadejda_test'
}
connection = psycopg2.connect(**dict_connection)
cursor = connection.cursor()


def load_treeview():
    day_total_sum = 0
    tree_day_report.delete(*tree_day_report.get_children())
    cursor.execute("SELECT records_partner.name, records_record.order_type, records_record.amount, records_record.note "
                   "FROM records_record INNER JOIN records_partner ON records_record.partner_id = records_partner.id "
                   f"WHERE warehouse = 'P' and created_at = current_date "
                   "ORDER BY records_record.id")
    today_orders = cursor.fetchall()
    for current_row in today_orders:
        row = [el for el in current_row]
        row[1] = get_order_type_display(row[1])
        tree_day_report.insert('', 'end', values=row)
        if row[1] == 'Каса':
            day_total_sum += float(row[2])
    tree_day_report.insert('', 0, values=())
    tree_day_report.insert('', 1, values=('', 'Наличност каса:', day_total_sum))
    tree_day_report.insert('', 2, values=())


# clear data from main dictionary
def clear_main_dictionary():
    global main_dictionary
    main_dictionary = empty_dictionary.copy()
    return


# get balance of firms from database
def get_firm_data():
    connection.commit()
    main_dictionary['partner_name'] = firm_cb.get()
    if main_dictionary['partner_name'] == 'Доставчик':
        main_dictionary['partner_id'] = 1
        main_dictionary['open_balance'] = 0
    elif main_dictionary['partner_name'] == 'Клиент':
        main_dictionary['partner_id'] = 2
        main_dictionary['open_balance'] = 0
    else:
        partner_data = "SELECT id, type, balance FROM records_partner WHERE name = %s"
        cursor.execute(partner_data, [main_dictionary['partner_name']])
        data = cursor.fetchone()
        main_dictionary['partner_id'] = data[0]
        main_dictionary['partner_type'] = data[1]
        main_dictionary['open_balance'] = int(data[2])
    open_balance_label['text'] = main_dictionary['open_balance']
    return


# get order type
def get_order_type(selection):
    dict = {1: 'P',
            2: 'A',
            3: 'S',
            0: 'C',
            4: 'B'}

    return dict[selection]


## get pvc order
# def get_order(current_type):
#     date = datetime.now().month
#     month_dict = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI", 7: "VII", 8: "VIII", 9: "IX", 10: "X", 11: "XI",
#                   12: "XII"}
#     current_month = month_dict[date]
#
#     if current_type == 'A':
#         cursor.execute("SELECT month, al_counter FROM records_order")
#     elif current_type == 'G':
#         cursor.execute("SELECT month, glass_counter FROM records_order")
#     elif current_type == 'P':
#         cursor.execute("SELECT month, pvc_counter FROM records_order")
#
#     record = cursor.fetchone()
#     db_month, order_counter = record[0], record[1]
#
#     if current_month != db_month:
#         change_month = ("UPDATE records_order SET month = %s, al_counter = %s, glass_counter = %s, pvc_counter = %s")
#         new_month = (current_month, 1, 1, 1)
#         cursor.execute(change_month, new_month)
#         connection.commit()
#         order_counter = 1
#     main_dictionary['production_order'] = (f"{current_type}-{current_month}-{order_counter}")
#     return


# filter list of combobox when writing
def update_cb(event):
    a = event.widget.get()
    newvalues = [i for i in lst if i.lower().startswith(a.lower())]
    firm_cb['values'] = newvalues
    firm_cb.focus()
    return


# get name of firms from database for combobox
def list_combobox():
    cursor.execute("SELECT name FROM records_partner")
    rows = cursor.fetchall()
    lst = [i[0] for i in rows]
    lst.sort()
    return lst


# input open balance of selected firm in balance label
def getSelectedItem(event):
    load_treeview()
    main_dictionary['close_balance'] = ''
    close_balance_label['text'] = main_dictionary['close_balance']
    main_dictionary['amount'] = ''
    amount_entry.delete(0, 'end')
    get_firm_data()
    open_balance_label['text'] = main_dictionary['open_balance']
    return


# change selected radio button
def sel():
    current_type = ''
    main_dictionary['note'] = ''
    note_entry.delete(0, 'end')
    main_dictionary['amount'] = 0.0
    amount_entry.delete(0, 'end')
    main_dictionary['close_balance'] = ''
    close_balance_label['text'] = ''
    selection = radio_var.get()
    # if selection == 1:
    #     current_type = 'P'
    # elif selection == 2:
    #     current_type = 'A'
    # get_order(current_type)
    # note_entry.insert(0, main_dictionary['production_order'])
    return selection


# calculate close balance depending of radio button slection
def update_close_balance(event):
    get_firm_data()

    selection = radio_var.get()
    main_dictionary['order_type'] = get_order_type(selection)
    main_dictionary['amount'] = int(amount_entry.get())

    if main_dictionary['partner_name'] == 'Клиент':
        main_dictionary['close_balance'] = 0.0
    elif main_dictionary['partner_name'] == 'Доставчик':
        main_dictionary['close_balance'] = 0.0
        main_dictionary['amount'] = - int(amount_entry.get())
    else:
        if main_dictionary['open_balance'] != '' and main_dictionary['amount'] != '':
            if main_dictionary['order_type'] in ['P', 'A', 'S']:
                main_dictionary['close_balance'] = main_dictionary['open_balance'] - main_dictionary['amount']
            else:
                main_dictionary['close_balance'] = main_dictionary['open_balance'] + main_dictionary['amount']
        else:
            main_dictionary['close_balance'] = ''
    close_balance_label['text'] = main_dictionary['close_balance']
    return


# show firm report
def firm_report():
    connection.commit()
    partner_number = "SELECT id FROM records_partner WHERE name = %s"
    firm = (firm_cb.get(),)
    cursor.execute(partner_number, firm)
    p_id = cursor.fetchone()
    f_report = ("SELECT records_record.created_at, records_record.warehouse, records_partner.name, "
                "records_record.order_type, records_record.amount, records_record.balance, records_record.note "
                "FROM records_record "
                "INNER JOIN records_partner ON records_record.partner_id = records_partner.id "
                "WHERE records_record.partner_id = %s "
                "ORDER BY records_record.id")
    cursor.execute(f_report, p_id)
    firm_balance = cursor.fetchall()

    firm_report_window = tk.Tk()
    firm_report_window.title('Справка за фирма')
    firm_report_window.geometry('750x630')
    def_font = tk.font.nametofont("TkDefaultFont")
    def_font.config(size=20)
    scrollbar = ttk.Scrollbar(firm_report_window, orient=tk.VERTICAL)

    tree_firm_report = ttk.Treeview(firm_report_window, height=25)
    scrollbar.configure(command=tree_firm_report.yview)
    tree_firm_report.configure(yscrollcommand=scrollbar.set)
    scrollbar.grid(row=0, rowspan=25, column=5, sticky="nsw")
    tree_firm_report.grid(row=0, rowspan=20, column=0, sticky='nw')
    style = ttk.Style()
    style.configure('Treeview', font=('Helvetica', 9))
    tree_firm_report['columns'] = ('date', 'warehouse', 'firm', 'order_type', 'amount', 'close_balance', 'note')
    tree_firm_report.column('#0', width=0)
    tree_firm_report.column('date', width=100, minwidth=20, anchor=tk.CENTER)
    tree_firm_report.column('warehouse', width=100, minwidth=50, anchor=tk.CENTER)
    tree_firm_report.column('firm', width=120, minwidth=50, anchor=tk.CENTER)
    tree_firm_report.column('order_type', width=80, minwidth=50, anchor=tk.CENTER)
    tree_firm_report.column('amount', width=50, minwidth=50, anchor=tk.CENTER)
    tree_firm_report.column('close_balance', width=50, minwidth=50, anchor=tk.CENTER)
    tree_firm_report.column('note', width=250, minwidth=50, anchor=tk.CENTER)

    tree_firm_report.heading('date', text='Дата', anchor=tk.CENTER)
    tree_firm_report.heading('warehouse', text='Склад', anchor=tk.CENTER)
    tree_firm_report.heading('firm', text='Фирма', anchor=tk.CENTER)
    tree_firm_report.heading('order_type', text='Вид запис', anchor=tk.CENTER)
    tree_firm_report.heading('amount', text='Сума', anchor=tk.CENTER)
    tree_firm_report.heading('close_balance', text='След', anchor=tk.CENTER)
    tree_firm_report.heading('note', text='Забележка', anchor=tk.CENTER)
    total_sum = 0.0

    for current_row in firm_balance[1:]:
        row = [el for el in current_row]
        row[1] = get_warehouse_display(row[1])
        row[3] = get_order_type_display(row[3])
        tree_firm_report.insert('', 'end', values=row)
        total_sum = int(row[5])

    tree_firm_report.insert('', 0, values=())
    tree_firm_report.insert('', 1, values=('', 'Крайно салдо:', total_sum))
    tree_firm_report.insert('', 2, values=())

    print_firm_report(firm_balance)

    tree_firm_report.mainloop()
    return


def print_firm_report(balance):
    print_report = [('Дата\t', 'Склад', 'Фирма', 'Вид запис', 'Сума', 'Крайно салдо', 'Забележка\n')]

    if len(balance) > 41:
        balance = balance[-41:]

    print_report.extend(balance)

    with open("C:\\Python\\Фирмен отчет.txt", 'w') as file:
        for row in range(len(print_report)):
            order = (list(print_report[row]))

            for index in range(len(order)):
                file.write(f"{str(order[index])}\t")

                if index != 0 and len(str(order[index])) < 8 and order[index] != "Продажба":
                    file.write("\t")

            file.write('\n')


# new firm window
def new_firm():
    # if note_entry.get() == '+++':
    #     partner_name = firm_cb.get()
    #     insert_new_partner = ("INSERT INTO records.partner (name, type, balance) VALUES (%s, %s, %s)")
    #     new_partner_data = (partner_name, 'Фирми', 0)
    #     cursor.execute(insert_new_partner, new_partner_data)
    #     connection.commit()
    return


# write in database end close entry_window
def ok_button():
    if firm_cb.get() not in list_combobox():
        messagebox.showinfo('Съобщение', 'Името не е в списъка на фирми!')
    else:
        main_dictionary['note'] = note_entry.get()

        insert_orders = ("INSERT INTO records_record ("
                         "created_at, "
                         "warehouse, "
                         "partner_id, "
                         "order_type, "
                         "amount, "
                         "balance, "
                         "note)"
                         "VALUES (%s, %s, %s, %s, %s, %s, %s)")
        order_data = (main_dictionary['date'],
                      main_dictionary['warehouse'],
                      main_dictionary['partner_id'],
                      main_dictionary['order_type'],
                      main_dictionary['amount'],
                      main_dictionary['close_balance'],
                      main_dictionary['note'])

        insert_partner_balance = "UPDATE records_partner SET balance = %s WHERE id = %s"
        partner_data = (main_dictionary['close_balance'], main_dictionary['partner_id'])

        cursor.execute(insert_orders, order_data)
        cursor.execute(insert_partner_balance, partner_data)

        # cursor.execute("SELECT pvc_counter, al_counter FROM records_order")
        # counters = cursor.fetchall()
        # pvc_counter, al_counter = int(counters[0][0]), int(counters[0][1])
        # if main_dictionary['order_type'] == 'P':
        #     pvc_counter += 1
        # if main_dictionary['order_type'] == 'A':
        #     al_counter += 1
        # insert_counts = "UPDATE records_order SET pvc_counter = %s, al_counter = %s"
        # current_counters = (pvc_counter, al_counter)
        # cursor.execute(insert_counts, current_counters)
        connection.commit()

        load_treeview()
        firm_cb.set('')
        open_balance_label['text'] = ''
        amount_entry.delete(0, 'end')
        radio_var.set(0)
        close_balance_label['text'] = ''
        note_entry.delete(0, 'end')
        clear_main_dictionary()
    return


# test th DB before start
def test_balances():
    connection.commit()

    for id in range(1000):
        f_report = ("SELECT records_partner.name, records_record.order_type, records_record.amount, "
                    "records_record.balance, records_partner.balance "
                    "FROM records_record "
                    "INNER JOIN records_partner ON records_record.partner_id = records_partner.id "
                    f"WHERE records_record.partner_id = {id} "
                    f"ORDER BY records_record.id")
        cursor.execute(f_report)
        firm_balance = cursor.fetchall()

        try:
            old_balance = firm_balance[0][3]
        except IndexError:
            continue

        if firm_balance[0][0] == 'Доставчик' or firm_balance[0][0] == 'Клиент':
            continue

        errors_one, errors_two = 0, 0
        balance, partner_balance = 0, 0

        for row in firm_balance[1:]:
            order_type, amount, balance, partner_balance = row[1], row[2], row[3], row[4]
            new_balance = old_balance + amount if order_type in ['C', 'B'] else old_balance - amount

            if int(balance) != new_balance:
                errors_one += 1

            old_balance = balance

        if balance != partner_balance:
            errors_two += 1

        if errors_one > 0 or errors_two > 0:
            messagebox.showinfo('Грешки в базата данни', f"{firm_balance[0][0]} - {errors_one}, {errors_two}")


# exit
def exit_button():
    cursor.close()
    connection.close()
    entry_window.destroy()
    return


def get_warehouse_display(warehouse):
    dict = {'A': 'Алуминий',
            'G': 'Стъклопакети',
            'P': 'PVC',
            'O': 'Поръчки',
            'M': 'Управител',
            }
    return dict[warehouse]


def get_order_type_display(order_type) -> str:
    dict = {'A': 'Поръчка Al',
            'G': 'Поръчка пакети',
            'P': 'Поръчка PVC',
            'S': 'Продажба',
            'C': 'Каса',
            'B': 'Банка'
            }
    return  dict[order_type]


# create entry window
entry_window = tk.Tk()
entry_window.title('Склад PVC')
entry_window.geometry('1500x700')
def_font = tk.font.nametofont("TkDefaultFont")
def_font.config(size=20)

radio_var = tkinter.IntVar()
warehouse_label = ttk.Label(entry_window, width=20,
                            text=(f"Склад: {get_warehouse_display(main_dictionary['warehouse'])}"),
                            anchor="c", font=('Helvetica', 20))
warehouse_label.grid(row=0, column=0, padx=20, pady=20)
warehouse_label.configure(background='Light Grey')
date_label = ttk.Label(entry_window, width=20, text=(main_dictionary['date']), anchor="c", font=('Helvetica', 20))
date_label.grid(row=0, column=1)
date_label.configure(background='Light Grey')

firm_label = ttk.Label(entry_window, text='Фирма', font=('Helvetica', 20))
firm_label.grid(row=1, column=0, padx=40, pady=5)

lst = list_combobox()
firm_cb = ttk.Combobox(entry_window, width=25, values=lst, font=('', 20), height=20)
firm_cb.grid(row=1, column=1, sticky="w", padx=40, pady=20)
entry_window.option_add('*TCombobox*Listbox.font', ('Helvetica', 15))
firm_cb.bind('<KeyRelease>', update_cb)
firm_cb.bind('<<ComboboxSelected>>', getSelectedItem)
# order_radio = ttk.Radiobutton(entry_window, text="PVC", variable=radio_var, value=1, command=sel)
# order_radio.grid(row=3, column=0, sticky="w", padx=40)
# al_radio = ttk.Radiobutton(entry_window, text="Al", variable=radio_var, value=2, command=sel)
# al_radio.grid(row=4, column=0, sticky="w", padx=40)
sell_radio = ttk.Radiobutton(entry_window, text="Продажба", variable=radio_var, value=3, command=sel)
sell_radio.grid(row=5, column=0, sticky="w", padx=40)
cash_radio = ttk.Radiobutton(entry_window, text="Каса", variable=radio_var, value=0, command=sel)
cash_radio.grid(row=5, column=0, sticky="e", padx=40)
# bank_radio = ttk.Radiobutton(entry_window, text="Банка", variable=radio_var, value=4, command=sel)
# bank_radio.grid(row=5, column=0, sticky="e", padx=40)

open_balance_label = ttk.Label(entry_window, width=10, text='', font=('Helvetica', 20))
open_balance_label.grid(row=2, column=1, sticky="e", padx=40)
open_balance_label_text = ttk.Label(entry_window, text='Hачално салдо:', font=('Helvetica', 20))
open_balance_label_text.grid(row=2, column=1, sticky="w", padx=40)
close_balance_label = ttk.Label(entry_window, width=10, text='', font=('Helvetica', 20))
close_balance_label.grid(row=6, column=1, sticky="e", padx=40)
close_balance_label_text = ttk.Label(entry_window, text='Крайно салдо:', font=('Helvetica', 20))
close_balance_label_text.grid(row=6, column=1, sticky="w", padx=40)

amount_entry = ttk.Entry(entry_window, width=10, font=('Helvetica', 20))
amount_entry.grid(row=4, column=1, sticky="w", padx=40)
amount_entry.bind('<KeyRelease>', update_close_balance)

note_label = ttk.Label(entry_window, text='Забележка:', font=('Helvetica', 20))
note_label.grid(row=8, column=0, padx=40, pady=20)
note_entry = ttk.Entry(entry_window, width=25, font=('Helvetica', 20))
note_entry.grid(row=8, column=1, sticky="w", padx=40)

new_firm_button = ttk.Button(entry_window, width=18, text='Нова фирма', command=new_firm)
new_firm_button.grid(row=9, columnspan=2, column=0, sticky="w", padx=45, pady=20)
firm_report_button = ttk.Button(entry_window, width=18, text='Фирмен отчет', command=firm_report)
firm_report_button.grid(row=9, columnspan=2, column=0, sticky="e", padx=40, pady=20)
ok_button = ttk.Button(entry_window, width=8, text='OK', command=ok_button)
ok_button.grid(row=10, columnspan=2, column=0, sticky="w", padx=192, pady=20)
cancel_button = ttk.Button(entry_window, width=8, text='Изход', command=exit_button)
cancel_button.grid(row=10, columnspan=2, column=0, sticky="e", padx=190, pady=20)

# day_report
scrollbar = ttk.Scrollbar(entry_window, orient=tk.VERTICAL)
tree_day_report = ttk.Treeview(entry_window, height=30)
tree_day_report['show'] = 'headings'
scrollbar.configure(command=tree_day_report.yview)
tree_day_report.configure(yscrollcommand=scrollbar.set)
scrollbar.grid(row=0, rowspan=15, column=5, sticky="nsw")
tree_day_report.grid(row=0, rowspan=20, column=4, sticky='ne')
style = ttk.Style()
style.configure('Treeview', font=('Helvetica', 10))
tree_day_report['columns'] = ('firm', 'action', 'amount', 'note')
tree_day_report.column('firm', width=150, minwidth=50, anchor=tk.CENTER)
tree_day_report.column('action', width=100, minwidth=50, anchor=tk.CENTER)
tree_day_report.column('amount', width=80, minwidth=50, anchor=tk.CENTER)
tree_day_report.column('note', width=320, minwidth=50, anchor=tk.CENTER)
tree_day_report.heading('firm', text='Фирма', anchor=tk.CENTER)
tree_day_report.heading('action', text='Действие', anchor=tk.CENTER)
tree_day_report.heading('amount', text='Сума', anchor=tk.CENTER)
tree_day_report.heading('note', text='Забележка', anchor=tk.CENTER)

# test_balances()
load_treeview()
entry_window.mainloop()
