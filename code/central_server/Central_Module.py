from threading import Thread
import queue
import socket
from EC_Module import erasure
from Ray_Module import ray_control
import os

message_queue = queue.Queue()

listen_ip = '0.0.0.0'
listen_port = 9999

web_ip = '172.31.70.50'
web_port = 10000
split_char="%$$%@#!#(*%^&%"


def listenning():
    sock_listen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock_listen.bind((listen_ip, listen_port))
        sock_listen.listen(1)
        print('central等待连接并接收命令')
        while True:
            print('准备接受下一条命令')
            conn, addr = sock_listen.accept()
            print('central连接已建立: ',addr)

            message = b''
            while True:
                # print(len(content))
                # file.write(content)
                buffer = conn.recv(4096)
                message = message + buffer
                print('传输中：', message)
                if len(buffer) < 4096:
                    break
                print('3')



            # buffer = conn.recv(4096)
            print('收到命令buffer')
            message = message.split(split_char.encode('utf-8'))  # 上传图片时会在转换成utf-8时出错
            print('命令是：')
            print('message:', message)

            if message[0] == b'Upload':  # 上传：Upload,file_id,filename,content
                message[0] = message[0].decode('utf-8')
                message[1] = message[1].decode('utf-8')
                print(message[1])
                message[2] = message[2].decode('utf-8')
                file_name = os.path.join('/root/Project/Central_server/uploadfile',message[2])
                content = message[3]

                print('上传的文件内容是')
                print(content)
            
                with open(os.path.join(file_name), 'wb') as file:
                    # while True:
                    #     print(len(content))
                    #     file.write(content)
                    #     content = conn.recv(4096)
                    #     if len(content) < 4096:
                    #         break
                    #     print('3')
                    file.write(content)
                        
                # while content:
                #     content = conn.recv(4096)
                #     print(content)
                print('已写入本地')
                message[3] = os.path.join('uploadfile',file_name)
                message = message[0:4]
                message_queue.put(message)
                print('upload message 已经入队')
                print(message)
            
            
            elif message[0] == b'Download':  # 下载：download,file_id,filename
                message[0] = message[0].decode('utf-8')
                message[1] = message[1].decode('utf-8')
                message[2] = message[2].decode('utf-8')
                message_queue.put(message)
                print('download message 已经入队')

            elif message[0] == b'Delete':  # 删除：Delete,file_id,filename
                message[0] = message[0].decode('utf-8')
                message[1] = message[1].decode('utf-8')
                message[2] = message[2].decode('utf-8')
                message_queue.put(message)
                print('Delete message 已经入队')

            else:
                print('未定义消息')
                send_message_to_web('fail')
            
    # except Exception as e:
    #     print(e)
    
    # except OSError:
    #     print('socket error')

    finally:
        sock_listen.close()

def handle_web_message():
    while True:
        if message_queue.empty():
            pass
        else:
            print('handle message')
            message = message_queue.get()

            if message[0] == 'Upload':
                print(message)
                if FileUpload(message[1], message[2], message[3]):
                    print('upload success')

            elif message[0] == 'Download':
                if FileDownload(message[1],message[2]):
                    print('download success')

            elif message[0] == 'Delete':
                if FileDelete(message[1],message[2]):
                    print('Delete success')
                # if remove(message[1],message[2]):

            else:
                raise Exception('未定义操作')
            


def send_message_to_web(message):
    sock_web = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock_web.connect((web_ip, web_port))
        sock_web.sendall(message.encode('utf-8'))

    # except OSError:
    #     print(type(sock_web))

    finally:
        sock_web.close()


def FileUpload(fileid, filename, file_path):  # filepath 要上传的文件存储在中央服务器的地址
    print("开始上传")
    if erasure('Upload' + split_char + file_path + split_char + fileid) is False:
        print('存储模块碎片文件存入缓冲区错误')
        send_message_to_web('Upload fail')
        return False
    # if ray_control('Upload' + ',' + file_path+","+fileid) is False:
    #     print('Ray模块标签存入缓冲区错误')
    #     send_message_to_web('Upload fail')
    #     return False
    if erasure('Commit' + split_char + 'None' + split_char +fileid + split_char + 'Upload') is False:
        print('存储模块握手错误')
        send_message_to_web('Upload fail')
        return False
    # 这三行放入EC_Module
    # if ray_control('Commit'+',None'+','+fileid) is False:
    #     print('ray commit error')
    #     return False
    send_message_to_web('Upload success')
    return True


def FileDownload(file_id, filename):
    file_path = os.path.join('/root/Project/Central_server/downloadfile', filename)
    if not erasure('Download' + split_char +file_path+ split_char +file_id):
        send_message_to_web('download error')
        return False

    sock_web = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('开始下载')
    
    try:
        sock_web.connect((web_ip, web_port))
        # 打开要发送的文件
        with open(file_path, 'rb') as file:
            # 读取文件内容
            data = file.read()
            # 发送文件数据
            sock_web.sendall(data)
        print("文件发送完成")
    # except OSError:
    #     print('socket error')
    finally:
        sock_web.close()
    return True

def FileDelete(fileid, filename):
    if erasure('Delete' + split_char + '' + split_char +fileid) is False:
        print('存储模块删除命令存入缓冲区错误')
        send_message_to_web('Delete fail')
        return False
    
    # if ray_control('Delete' + split_char + file_path + split_char +fileid) is False:
    #     print('Ray模块删除命令存入缓冲区错误')
    #     send_message_to_web('Delete fail')
    #     return False
    
    print('')
    if erasure('Commit' + split_char + 'None' + split_char + fileid + split_char + 'Delete') is False:
        print('存储模块握手错误')
        send_message_to_web('Delete fail')
        return False
    # 这三行放入EC_Module
    # if ray_control('Commit'+',None'+','+fileid) is False:
    #     print('ray commit error')
    #     return False
    send_message_to_web('Delete success')
    return True

# message_queue = queue.Queue()
# sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# # Example
# message_queue.put("Upload,test.txt")
if __name__ == "__main__":
    listen_thread = Thread(target=listenning)
    handle_thread = Thread(target=handle_web_message)
    listen_thread.start()
    handle_thread.start()
    listen_thread.join()
    handle_thread.join()
