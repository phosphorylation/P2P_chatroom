import select
import socket
import sys
import random
from helper import send_message
from helper import receive_message
from helper import encryption_gen_sym
from helper import encryption_recv_sym
from threading import Thread


def send_msg():
    while True:
        
        message = sys.stdin.readline().rstrip('\n')
        if message == "Exit()":
            print("Connection closed")
            # close connection with central server
            client_socket.send((send_message(message, sym_key_with_central_server)))
            client_socket.close()
            # close connection with all other clients
            for j in client_dic:
                sym_key = client_dic[j]["key"]
                j.send(send_message(message, sym_key))
                j.send(send_message(username + " has left the server", sym_key))

            sys.exit()
        else:
            for j in client_dic:
                sym_key = client_dic[j]["key"]
                j.send(send_message(username + ": " + message, sym_key))
            prompt()


def recv_msg():
    while True:
        sym_key = client_dic[i]["key"]
        other_message = receive_message(i, sym_key)

        # the other client wants to leave
        if other_message == "Exit()":
            second_message = receive_message(i, sym_key)
            sys.stdout.write('\n' + second_message + '\n')
            del client_dic[i]
            socket_list.remove(i)
            i.close()

        # normal message
        else:
            sys.stdout.write('\n' + other_message + '\n')
        prompt()

def prompt():
    sys.stdout.write('You: ')
    sys.stdout.flush()


server_PORT = 5001
client_PORT_recv_msg = 5002 + int(random.random()*100)
IP = "127.0.0.1"


# server socket listening to other clients
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# allow to reconnect to the same port
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(('', client_PORT_recv_msg))
server_socket.listen(10)


# client connecting to server
server_host = input("Please Enter Server IP Address: ")
username = input("Create Your Username: ")
room_number = input("Enter the room number you want to join: ")
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((server_host, server_PORT))
print("Connect to central server successfully. ")
print("-----Enter 'Exit()' to leave anytime-----")
sym_key_with_central_server = encryption_gen_sym(client_socket)
client_socket.send(send_message(room_number, sym_key_with_central_server))     # send room number
client_socket.send(send_message(str(client_PORT_recv_msg), sym_key_with_central_server))     # send client's port for receiving message


# ____________________________________________________________________

socket_list = [socket.socket(), server_socket, client_socket]    # store all the sockets
client_dic = {}     # store all other clients' info
prompt()
if __name__ == '__main__':
    client_dic={}
    Thread(target=send_msg, args=()).start()
    Thread(target=recv_msg, args=()).start()
    while True:
        read_sockets, _, _ = select.select(socket_list, [], [])

        for i in read_sockets:
            if i == server_socket:      # other clients tries to connect to me, since I am new
                connecting_socket, connecting_address = server_socket.accept()
                sym_key_with_client = encryption_recv_sym(connecting_socket)
                socket_list.append(connecting_socket)
                client_dic[connecting_socket] = {"key": sym_key_with_client}
                # tells the old senders that I have joined
                connecting_socket.send(send_message(username + " has joined the room.", sym_key_with_client))

            elif i == client_socket:    # the server tells me to connect to new client
                new_ip = receive_message(i, sym_key_with_central_server)
                new_port = int(receive_message(i, sym_key_with_central_server))
                new_socket_to_other = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                new_socket_to_other.connect((new_ip, new_port))
                sym_key_with_server = encryption_gen_sym(new_socket_to_other)
                socket_list.append(new_socket_to_other)
                client_dic[new_socket_to_other] = {"key": sym_key_with_server}


        # elif i == sys.stdin:            # send message to other clients
        #     message = sys.stdin.readline().rstrip('\n')
        #
        #     # client wants to end the connection
        #     if message == "Exit()":
        #         print("Connection closed")
        #         # close connection with central server
        #         client_socket.send((send_message(message, sym_key_with_central_server)))
        #         client_socket.close()
        #         # close connection with all other clients
        #         for j in client_dic:
        #             sym_key = client_dic[j]["key"]
        #             j.send(send_message(message, sym_key))
        #             j.send(send_message(username + " has left the server", sym_key))
        #
        #         sys.exit()
        #
        #     # normal input from terminal
        #     else:
        #         for j in client_dic:
        #             sym_key = client_dic[j]["key"]
        #             j.send(send_message(username + ": " + message, sym_key))
        #         prompt()
        #
        # else:       # message from existing client, print it out
        #     sym_key = client_dic[i]["key"]
        #     other_message = receive_message(i, sym_key)
        #
        #     # the other client wants to leave
        #     if other_message == "Exit()":
        #         second_message = receive_message(i, sym_key)
        #         sys.stdout.write('\n' + second_message + '\n')
        #         del client_dic[i]
        #         socket_list.remove(i)
        #         i.close()
        #
        #     # normal message
        #     else:
        #         sys.stdout.write('\n' + other_message + '\n')
        #     prompt()

