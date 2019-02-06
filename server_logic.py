import socket
import threading


class ServerLogic:
    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.setblocking(0)
        self.port_no = 2345
        self.server_ip = socket.gethostbyname(socket.gethostname())
        self.error_msg = ''
        self.error_occured = False
        self.client_connected = False
        self.server_running = False
        self.client_list = {}
        return

    def startServer(self):
        try:
            self.server_socket.bind((self.server_ip, self.port_no))
            self.server_running = True
            threading.Thread(target=self.mainServerThread).start()
        except socket.error as err:
            self.error_occured = True
            self.error_msg = err
            return False
        return True

    def getIPAddress(self):
        return str(self.server_ip)

    def isErrorOccured(self):
        return self.error_occured

    def errorMessage(self):
        return self.error_msg

    def mainServerThread(self):
        while (self.server_running):
            try:
                self.msg, self.address = self.server_socket.recvfrom(2048)
                self.msg = self.msg.decode('ascii')
                self.handleClient()
            except socket.error:
                pass

    def isClientConnected(self):
        return self.client_connected

    def clientConnectedStatus(self, status):
        self.client_connected = status

    def serverStatus(self):
        return self.server_running

    def getClientName(self):
        return self.client_name

    def shutDownServer(self):
        self.server_running = False
        return

    def handleClient(self):
        if '1111' in self.msg:
            temp_list = self.msg.split('||')
            self.client_name = temp_list[1]
            self.client_list[self.client_name] = self.address
            self.server_socket.sendto('Welcome to Chat'.encode('ascii'), self.address)
            self.updateClientList()
            self.client_connected = True
        elif '0000' in self.msg:
            temp_list = self.msg.split('||')
            self.client_name = temp_list[1]
            self.client_list.pop(self.client_name)
            if len(self.client_list) == 1:
                for k in self.client_list.keys():
                    self.server_socket.sendto('Empty List 0000'.encode('ascii'), self.client_list[k])
            else:
                self.updateClientList()
        else:
            msg_disect_list = self.msg.split('||')
            i = 2
            while i < len(msg_disect_list):
                self.server_socket.sendto((msg_disect_list[0] + '>>' + msg_disect_list[1]).encode('ascii'), self.client_list[msg_disect_list[i]])
                i = i+1
        pass

    def updateClientList(self):
        if len(self.client_list) > 1:
            client_names = self.client_list.keys()
            spl_msg = ''
            for k in client_names:
                spl_msg = spl_msg + k + '||'
            spl_msg = spl_msg + '1111'

            for g in client_names:
                self.server_socket.sendto(spl_msg.encode('ascii'), self.client_list[g])
        pass

    def sendServerShutDownMsg(self):
        for k in self.client_list.keys():
            self.server_socket.sendto('Server Offline 0101'.encode('ascii'), self.client_list[k])
