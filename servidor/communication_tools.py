import socket
import base64
from logs import logs

def send_json(sockets, value, sock):
    chunk = bytearray()
    chunk.extend((0).to_bytes(4, 'big'))
    str_value = str(value)
    msg_bytes = str_value.encode("utf-8", "ignore")
    length = len(msg_bytes)
    chunk.extend((length).to_bytes(4, 'little'))
    chunk.extend(msg_bytes)
    sock.sendall(chunk)
    id_ = sockets[sock]["id"]
    user = ""
    if "username" in sockets[sock].keys():
        user = sockets[sock]["username"]
    if type(value) == dict:
        tipo = value["type"]
        logs(id_, user, 13, (tipo, f"Largo: {length} bytes"))
    else:
        for data in value:
            tipo = data["type"]
            logs(id_, user, 13, (tipo, f"Largo: {length} bytes"))

def prepare_img(path, id_img):
    chunk = bytearray()
    with open(path, "rb") as img:
        img_bytes = base64.b64encode(img.read())
    id_ = (id_img).to_bytes(4, 'big')
    length = (len(img_bytes)).to_bytes(4, 'little')
    chunk.extend(id_)
    chunk.extend(length)
    chunk.extend(img_bytes)
    return chunk