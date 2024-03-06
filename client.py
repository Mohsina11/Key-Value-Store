from fastapi import FastAPI, HTTPException,Request
from worker import delete_expired_key
import sys, socket
import time
import uvicorn
import ast

app = FastAPI()

def get_socket():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    return sock
 
if len(sys.argv) != 4:
    print ("Please Initiate in the above format: script, Server IP address, Server port number,Client Port Number")
    exit()

server_ip_address = str(sys.argv[1])
server_port = int(sys.argv[2])
client_port=int(sys.argv[3])

server = get_socket()
server.connect((server_ip_address, server_port))

def listen_for_messages():
    while True:
        output = server.recv(2048).decode()
        print(output)

@app.post('/save/{key}')
async def save_data(key: str,request:Request):
    data = await request.json()
    value = data.get("value")
    ttl=data.get("ttl")
    request_id = int(time.time()*1000)
    if value is None:
        raise HTTPException(400, detail='Bad Request: "value" must be provided in the request body')
    command = f"set {key} {value}"+ ' ' + str(request_id)
    server.send(command.encode())
    response = server.recv(2048).decode()
    print(response)
    if ttl is not None:
        delete_expired_key.schedule(args=(key,), kwargs=None, delay=ttl)
    if response is None:
        raise HTTPException(500, detail='Internal Server Error')
    data = {
            "success":True,
            "request_id": response
    }
    return data


@app.get('/get/{key}')
async def get_data(key: str):
    req_id = int(time.time()*1000)
    command = f"get {key}" 
    print(command)
    command = command + ' ' + str(req_id)
    server.send(command.encode())
    response = server.recv(2048).decode()
    if response is None:
        raise HTTPException(500, detail='Key Not Found')
    elif response=='Error: Non existent key':
        raise HTTPException(400,detail='Key Not Found')
    response_tuple = ast.literal_eval(response)
    data = {
            "success":True,
            "value": response_tuple[0],
            "request_id": response_tuple[1]
    }
    return data

@app.delete('/delete/{key}')
async def delete_data(key: str):
    req_id = int(time.time()*1000)
    command = f"del {key}"
    command = command + ' ' + str(req_id)
    server.send(command.encode())
    response = server.recv(2048).decode()
    print(response)
    if response is None:
        raise HTTPException(500, detail='Key Not Found')
    data = {
            "success":True,
            "request_id": req_id
    }
    return data


if __name__ == '__main__':
    uvicorn.run('client:app', host='0.0.0.0', port=client_port, reload=True)