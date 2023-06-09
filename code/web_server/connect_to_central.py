import os
import sys
import socket

sys.path.append(os.path.dirname(sys.path[0]))
import config
setting=config.args()
settings=setting.set
# 上传：Upload,file_id,filename,content
# 下载：Download,file_id,filename
# 删除：Delete,file_id,filename

listen_ip = settings["listen_ip"]
listen_port = settings["web_listen_central"]
central_ip = settings["central_ip"]
central_port = settings["web_send_central"]

split_char=settings["split_char"].encode("utf-8")

def upload_to_central(fileid, filename, file):
    print("upload进程pid是" + str(os.getpid()))
    sock_listen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock_central = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock_central.connect((central_ip, central_port))
        print('已连接到central server')
        content = file.read()
        print('content长度:', len(content))
        message = b'' + b'Upload' + split_char + str(fileid).encode(
            'utf-8') + split_char + filename.encode('utf-8') + split_char + content
        # print(message)
        sock_central.sendall(message)
        print('已发送上传命令')
        # sock_central.close()

        sock_listen.bind((listen_ip, listen_port))
        sock_listen.listen(5)
        print('等待central server连接')

        conn, addr = sock_listen.accept()
        print('已连接到central server')
        message = conn.recv(1024)
        print('已接收到central server的回复')
        # sock_listen.close()
        if message == b'Upload success':
            print('上传成功')
            return True
        elif message == b'Upload fail':
            print('上传失败')
            return False
        return False
    except OSError as e:
        print(e)
        print(type(sock_central))
        print(type(sock_listen))
    finally:
        print(type(sock_central))
        print(sock_central)
        print(type(sock_listen))
        sock_central.close()
        sock_listen.close()


def download_to_central(fileid, filename, file_path):
    print("download进程pid是" + str(os.getpid()))
    sock_listen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock_central = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock_central.connect((central_ip, central_port))
        print('已连接到central server')
        message = b'' + b'Download' + split_char + str(fileid).encode(
            'utf-8') + split_char + filename.encode('utf-8')
        print(message)
        sock_central.sendall(message)
        print('已发送下载命令')
        # sock_central.close()

        sock_listen.bind((listen_ip, listen_port))
        sock_listen.listen(5)
        print('等待central server连接')

        conn, addr = sock_listen.accept()
        print('已连接到central server')

        content = b''

        while True:
            buffer = conn.recv(4096)
            content = b'' + content + buffer
            if len(buffer) < 4096:
                break

        if content == b'download error':
            print('下载失败')
            return False
        print('已接收到central server的回复')

        with open(file_path, 'wb') as f:
            f.write(content)

        print('下载成功')

        return True

        # sock_listen.close()

    except OSError as e:
        print(e)
        print(type(sock_central))
        print(type(sock_listen))
    finally:
        print(type(sock_central))
        print(sock_central)
        print(type(sock_listen))
        sock_central.close()
        sock_listen.close()


def Delete_to_central(fileid, filename):
    print("delete进程pid是" + str(os.getpid()))
    sock_listen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock_central = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock_central.connect((central_ip, central_port))
        print('已连接到central server')
        message = b'' + b'Delete' + split_char + str(fileid).encode(
            'utf-8') + split_char + filename.encode('utf-8')
        sock_central.sendall(message)
        print('已发送删除命令')
        # sock_central.close()

        sock_listen.bind((listen_ip, listen_port))
        sock_listen.listen(5)
        print('等待central server连接')

        conn, addr = sock_listen.accept()
        print('已连接到central server')
        message = conn.recv(1024)
        print('已接收到central server的回复')
        # sock_listen.close()
        if message == b'Delete success':
            print('删除成功')
            return True
        elif message == b'Delete fail':
            print('删除失败')
            return False
        return False
    except OSError as e:
        print(e)
        print(type(sock_central))
        print(type(sock_listen))
    finally:
        print(type(sock_central))
        print(sock_central)
        print(type(sock_listen))
        sock_central.close()
        sock_listen.close()