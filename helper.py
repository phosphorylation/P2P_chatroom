import encryption
import socket
HEADER_LENGTH = 10


def send_message(message, key):
    en_message = encryption.sym_encrypt(message.encode(), key)
    return f"{len(en_message):<{HEADER_LENGTH}}".encode() + en_message      # in bytes form


def receive_message(target_socket, key):
    try:
        message_header = target_socket.recv(HEADER_LENGTH)

        if not len(message_header):
            return False
        message_length = int(message_header.decode())

        p = target_socket.recv(message_length)
        de_message = encryption.sym_decrypt(p, key)

        return de_message.decode()  # return a message in string form

    except:
        print("Enable to receive")
        return False


def encryption_gen_sym(client_socket):       # client
    asy_key = encryption.asy_key_gen()  # generate asymmetric key
    client_public_key = asy_key.public_key()

    # receive server's public key
    server_public_key = encryption.bytes_to_key(client_socket.recv(2048))

    # generate common symmetric key
    sym_key = encryption.sym_key_gen()

    # encrypt symmetric key with server's public key
    encrypted_sym_key = encryption.asy_encrypt(sym_key, server_public_key)
    client_socket.send(encrypted_sym_key)

    return sym_key


def encryption_recv_sym(server_socket):     # server
    asy_key = encryption.asy_key_gen()  # generate asymmetric key
    server_public_key = asy_key.public_key()

    # send server's public key
    server_socket.send(encryption.key_to_bytes(server_public_key))

    # receive common symmetric key
    encrypted_sym_key = server_socket.recv(2048)

    # decrypt to get symmetric key using server's public key
    sym_key = encryption.asy_decrypt(encrypted_sym_key, asy_key)

    return sym_key
