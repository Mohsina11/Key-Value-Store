from huey import RedisHuey
import socket
import time

huey = RedisHuey('distributedkvstore', host='localhost', port=6379)
def get_socket():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
    return sock
 
server_ip_address = '127.0.0.1'
server_port = 5004

server = get_socket()
server.connect((server_ip_address, server_port))

@huey.task()
def delete_expired_key(data:any):
    req_id = int(time.time()*1000)
    command = f"del {data}"
    command = command + ' ' + str(req_id)
    server.send(command.encode())
    server.recv(2048).decode()
    return