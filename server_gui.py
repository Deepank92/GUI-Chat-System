import tkinter as tk
from tkinter import scrolledtext
from tkinter.ttk import Button
from tkinter import messagebox
from server_logic import ServerLogic
import threading

class ServerGUI:
    def __init__(self):
        self.server = ServerLogic()
        self.root = tk.Tk()
        self.root.resizable(height=False, width=False)
        self.root.geometry('800x600')
        self.root.title('Chat Server')
        self.createGUI()
        self.root.protocol('WM_DELETE_WINDOW', self.onShuttingDownServer)
        self.root.mainloop()

    def createGUI(self):
        tk.ttk.Style().configure('TButton', font=('Times New Roman', 16))

        self.server_status_box = scrolledtext.ScrolledText(self.root, font=('Times New Roman', 16),
                                                           undo=True, height=24, width=71)
        self.server_status_box.grid(row=0, column=0)

        self.start_server_btn=Button(self.root, text='Start Server', command=self.startServerBtnClickEvent)
        self.start_server_btn.grid(row=1, column=0, rowspan=2, sticky='W')



    def startServerBtnClickEvent(self):
        self.server_status_box.insert(tk.END, 'Starting Server...\n')
        if self.server.startServer():
            self.server_status_box.insert(tk.END, 'Server Started Successfuly!!!\n')
            self.server_status_box.insert(tk.END, 'Server IP Address is::'+self.server.getIPAddress() + '\n')
            threading.Thread(target=self.updateGUI).start()
        elif self.server.isErrorOccured():
            messagebox.showerror('Message From Server', self.server.errorMessage())
            self.server_status_box.insert(tk.END, 'Server Failed To Start...\n')
        return

    def updateGUI(self):
        while self.server.serverStatus():
            if self.server.isClientConnected():
                self.server_status_box.insert(tk.END, self.server.getClientName() + ' has been Connected!!!\n')
                self.server.clientConnectedStatus(False)

    def onShuttingDownServer(self):
        self.server.sendServerShutDownMsg()
        self.server.shutDownServer()
        self.root.destroy()
        return


