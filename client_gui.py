import tkinter as tk
from tkinter.ttk import Frame
from tkinter.ttk import Entry
from tkinter.ttk import Label
from tkinter.ttk import Button
from tkinter import scrolledtext
from tkinter import Listbox
from tkinter import messagebox
import socket
import threading

class ClientGUI:
    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_socket.settimeout(5.0)
        self.port = 2345
        self.client_running = False
        self.client_connected = False
        self.root = tk.Tk()
        self.root.resizable(width=False, height=False)
        self.root.title('Chat Client')
        self.createGUI()
        self.root.protocol('WM_DELETE_WINDOW', self.onShuttingDownClient)
        self.root.mainloop()
        return

    def createGUI(self):
        tk.ttk.Style().configure('TLabel', font=('Times New Roman', 16))
        tk.ttk.Style().configure('TButton', font=('Times New Roman', 16))
        self.frame = Frame(self.root)

        self.user_name_label = Label(self.frame, text='User Name')
        self.user_name_label.grid(row=0, column=0, sticky='W')

        self.user_name_box = Entry(self.frame, font=('Times New Roman', 16), width=20)
        self.user_name_box.grid(row=0, column=1)

        self.ip_label = Label(self.frame, text='Server IP Address')
        self.ip_label.grid(row=1, column=0, sticky='W')

        self.ip_addr_box = Entry(self.frame, font=('Times New Roman', 16))
        self.ip_addr_box.grid(row=1, column=1)

        self.connect_btn = Button(self.frame, text='Connect', command=self.connectBtnClick)
        self.connect_btn.grid(row=2, column=0, sticky='W')

        self.chat_area = scrolledtext.ScrolledText(self.frame, height=10, width=42, undo=True,
                                                   font=('Times New Roman', 16))
        self.chat_area.grid(row=3, column=0, sticky='NEWS')
        self.chat_area.configure(state='disabled')

        self.client_list = Listbox(self.frame, font=('Times New Roman', 16), selectmode=tk.MULTIPLE)
        self.client_list.grid(row=3, column=1, sticky='NEWS')

        self.msg_box = scrolledtext.ScrolledText(self.frame, font=('Times New Roman', 16), height=1, width=42, undo=True)
        self.msg_box.grid(row=4, column=0, sticky='W')

        self.send_btn = Button(self.frame, text='Send', command=self.sendBtnClick)
        self.send_btn.grid(row=4, column=1, sticky='W')
        self.send_btn.state(['disabled'])

        self.frame.grid(row=0, column=0)
        return

    def connectBtnClick(self):
        self.client_name = self.user_name_box.get()
        if not (len(self.client_name) == 0):
            try:
                self.client_socket.sendto(('1111||'+ self.client_name).encode('ascii'), (self.ip_addr_box.get(), self.port))
                self.message, self.address = self.client_socket.recvfrom(2048)
                self.chat_area.config(state='normal')
                self.chat_area.insert(tk.END, self.message.decode('ascii') + '\n')
                self.chat_area.config(state='disabled')
                self.client_running = True
                threading.Thread(target=self.updateClientList).start()
                self.connect_btn.state(['disabled'])
                self.user_name_box.state(['disabled'])
                self.ip_addr_box.state(['disabled'])
                self.send_btn.state(['!disabled'])
                self.client_connected = True
            except socket.timeout as tout:
                messagebox.showerror("Message From Client", tout)
            except socket.gaierror as gerror:
                messagebox.showerror("Message From Client", gerror)
                pass
            pass
        else:
            messagebox.showerror('Message From Client', 'User Name cannot be empty')

    def sendBtnClick(self):
        recv_clients_list = self.client_list.curselection()
        msg_type = ''
        if len(recv_clients_list) > 1:
            msg_type = ' [MC]'
        recv_clients = ''
        for k in recv_clients_list:
            recv_clients = recv_clients + '||' + self.client_list.get(k)
        self.message_to_sent = self.client_name + '||' + self.msg_box.get(1.0, tk.END) + msg_type + recv_clients
        self.chat_area.config(state='normal')
        self.chat_area.insert(tk.END, 'You>>' + self.msg_box.get(1.0, tk.END) + '\n')
        self.chat_area.config(state='disabled')
        self.client_socket.sendto(self.message_to_sent.encode('ascii'), (self.ip_addr_box.get(), self.port))
        self.msg_box.delete(1.0, tk.END)
        pass

    def onShuttingDownClient(self):
        if self.client_connected:
            self.client_socket.sendto(('0000' + '||' + self.client_name).encode('ascii'), (self.ip_addr_box.get(), self.port))
        self.client_running = False
        self.root.destroy()
        pass

    def updateClientList(self):
        self.client_socket.setblocking(0)
        while self.client_running:
            try:
                self.message, self.address = self.client_socket.recvfrom(2048)
                self.message = self.message.decode('ascii')
                i = 0
                j = 0
                if self.isContain(self.message, '1111'):
                    temp_client_list = self.message.split('||')
                    self.client_list.delete(0, tk.END)
                    while i < len(temp_client_list):
                        if not (self.client_name == temp_client_list[i]) and not (temp_client_list[i] == '1111'):
                            self.client_list.insert(j, temp_client_list[i])
                            j = j + 1
                        i = i+1
                elif 'Empty List 0000' in self.message:
                    self.client_list.delete(0, tk.END)
                elif 'Server Offline 0101' in self.message:
                    self.client_connected = False
                    self.chat_area.config(state='normal')
                    self.chat_area.insert(tk.END, 'Server is Offline. Chat discontinues!!!\n')
                    self.chat_area.config(state='disabled')
                    self.send_btn.state(['disabled'])
                    self.connect_btn.state(['!disabled'])
                    self.ip_addr_box.state(['!disabled'])
                    self.user_name_box.state(['!disabled'])
                    self.client_socket.settimeout(1)
                    self.client_running = False
                else:
                    self.chat_area.config(state='normal')
                    self.chat_area.insert(tk.END, self.message + '\n')
                    self.chat_area.config(state='disabled')
            except socket.error:
                pass
        pass

    def isContain(self, str, sub_str):
        index = str.find(sub_str)
        if index == -1:
            return False
        else:
            return True