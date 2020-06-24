import socket
import select
from helper import send_message
from helper import receive_message
from helper import encryption_gen_sym
from helper import encryption_recv_sym

server_PORT = 5001
IP = "127.0.0.1"

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# allow to reconnect to the same port
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(('', server_PORT))
server_socket.listen(10)
socket_list = [server_socket]   # keep updating
client_dic = {}
print("Central server starts running......")

while True:
    read_sockets, _, _ = select.select(socket_list, [], [])

    for i in read_sockets:
        if i == server_socket:     # new connection
            connecting_socket, connecting_address = server_socket.accept()
            ip_address, port = connecting_address
            print("Accept new connection from: " + str(ip_address) + ": " + str(port))

            sym_key_with_client = encryption_recv_sym(connecting_socket)
            room_number = receive_message(connecting_socket, sym_key_with_client)
            client_port = receive_message(connecting_socket, sym_key_with_client)   # client's port for receiving message
            socket_list.append(connecting_socket)

            for j in client_dic:    # send the new client's ip address in existing dictionary
                if room_number == client_dic[j]["room"]:
                    j.send(send_message(str(ip_address), client_dic[j]["key"]))
                    j.send(send_message(str(client_port), client_dic[j]["key"]))

            client_dic[connecting_socket] = {"room": room_number, "key": sym_key_with_client}   # add the new client to the dictionary

        else:   # existing connection
            sym_key_with_client = client_dic[i]["key"]
            message = receive_message(i, sym_key_with_client)

            # the client wants to leave
            if message == "Exit()":
                print("Some client has just left.")
                del client_dic[i]
                socket_list.remove(i)
                i.close()
