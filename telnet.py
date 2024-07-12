# Socket server in python using select function

import socket, select, json
from twitter_timeline import twiobj_lock, getTweets, banTwi

class telnet:
    CONNECTION_LIST = []    # list of socket clients
    server_socket = []
    timeout_list = {}
    timeout = 0
    con_timeout = 10
    livelogo = False
    schedule = False
    scheduletimer = 0
    RECV_BUFFER = 4096 # Advisable to keep it as an exponent of 2
    #PORT = 5000


    def __init__(self, ipaddr="127.0.0.1", port=5000, timeout=1):
        self.timeout = timeout
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # this has no effect, why ?
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((ipaddr, port))
        self.server_socket.listen(10)
        # Add server socket to the list of readable connections
        self.CONNECTION_LIST.append(self.server_socket)
        print "Telnet server started on "+str(ipaddr)+": " + str(port)

    def killCon(self, sock):
        try:
            sock.close()
            self.CONNECTION_LIST.remove(sock)
            del self.timeout_list[str(id(sock))]
        except:
            pass

    def killConId(self, sockid):
        for sock in self.CONNECTION_LIST:
            if (sockid == str(id(sock))):
                self.killCon(sock)
                break
 
    def parseCmd(self, data, sock):
        splitCmd = ""
        command=""
        try:
            splitCmd = data.split()
            command=splitCmd[0]
            del splitCmd[0]
        except:
            pass

        # parse no arguments commands
        if (len(splitCmd) == 0):
            if(command.lower() == "tweetslist"):
                try:
                    twiobj_lock.acquire()
                    sock.send(json.dumps(getTweets()))
                finally:
                    twiobj_lock.release()

        # commands with options
        elif (len(splitCmd) < 1):
            sock.send("No arguments provided for command %i \"%s\"\n" % (len(splitCmd),command))
        else:
            if(command.lower() == "livelogo"):
                if(splitCmd[0].lower() == 'on'):
                    self.livelogo = True
                elif (splitCmd[0].lower() == 'off'):
                    self.livelogo = False
                sock.send("%s set to %s\n" % (command, splitCmd[0]) )
            if(command.lower() == "schedule"):
                if(self.scheduletimer < 10500):
                    sock.send("NOK\n")
                else:
                    self.schedule = True
                    sock.send("OK\n")
            if(command.lower() == "bantwi"):
                    sock.send(banTwi(int(splitCmd[0])))

        self.killCon(sock)

    def do_work(self):
        # Get the list sockets which are ready to be read through select
        read_sockets,write_sockets,error_sockets = select.select(self.CONNECTION_LIST,[],[],self.timeout)
        #print "Select"
        #print self.timeout_list
        for sock in read_sockets:

            #New connection
            if sock == self.server_socket:
                # Handle the case in which there is a new connection recieved through server_socket
                sockfd, addr = self.server_socket.accept()
                self.CONNECTION_LIST.append(sockfd)
                print "Client (%s, %s) connected" % addr
                self.timeout_list[str(id(sockfd))] = 0

            #Some incoming message from a client
            else:
                # Data recieved from client, process it
                self.timeout_list[str(id(sock))] = 0
                try:
                    #In Windows, sometimes when a TCP program closes abruptly,
                    # a "Connection reset by peer" exception will be thrown
                    data = sock.recv(self.RECV_BUFFER)
                    # echo back the client message
                    if data:
                        self.parseCmd(data, sock)
 
                # client disconnected, so remove from socket list
                except:
                    #broadcast_data(sock, "Client (%s, %s) is offline" % addr)
                    #print "Client (%s, %s) is offline" % addr
                    self.killCon(sock)
                    continue
        keys = self.timeout_list.keys()
        for sockid in keys:
            self.timeout_list[sockid] += 1
            if(self.timeout_list[sockid] >= self.con_timeout):
                print "Kill con called"
                self.killConId(sockid)
        del keys
    def __del__(self):
        self.server_socket.close()