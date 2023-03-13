import imapclient
import os
import email
import chardet
import threading
import time
from email.header import decode_header
from DBot_SDK import send_message
from conf.experiment_info import ExperimentInfo
from utils import file_name_handler

class EMailServer:
    _email_server = None
    _email_address = ''
    _messages = []
    _auto_download_thread = None
    _auto_download_stop = True

    @classmethod
    def connect_email(cls, gid=None, qid=None, msg_list=[]):
        message_parts = []
        if gid:
            message_parts.append(f'[CQ:at,qq={qid}]')
        # 获取邮箱信息
        email_info = ExperimentInfo.get_email_info()
        cls._email_address = email_info.get('address', None)
        email_password = email_info.get('password', None)
        server_host = email_info.get('host', None)
        # 连接到IMAP服务器
        cls._email_server = imapclient.IMAPClient(server_host, ssl= True)
        cls._email_server.login(cls._email_address, email_password)
        cls._email_server.id_({"name": "IMAPClient", "version": imapclient.version.version})
        info = cls._email_server.select_folder('INBOX', readonly = True)
        send_message(f'登录{cls._email_address}成功', gid, qid)
    
    @classmethod
    def download_attachment_by_email_ids(cls, email_ids, gid, qid):
        if type(email_ids) is int:
            email_ids = [email_ids]
        for uid, message_data in cls._email_server.fetch(email_ids, 'RFC822').items():
            email_message = email.message_from_bytes(message_data[b'RFC822'])
            for part in email_message.walk():
                # 如果是附件
                if part.get_content_disposition() == 'attachment':
                    filename = part.get_filename()
                    if filename:
                        encoding = chardet.detect(decode_header(filename)[0][0])['encoding']
                        decoded_filename = decode_header(filename)[0][0].decode(encoding)
                        decoded_filename, time_info, group_id, experiment_id = file_name_handler(decoded_filename)
                        if decoded_filename:
                            print(decoded_filename)
                            folder_path = os.path.join(ExperimentInfo.get_save_path(), time_info, experiment_id)
                            file_path = os.path.join(folder_path, decoded_filename)
                            os.makedirs(folder_path, exist_ok=True)
                            send_message(f'{decoded_filename}\n下载成功', gid, qid)
                            # 下载附件
                            with open(file_path, 'wb') as f:
                                f.write(part.get_payload(decode=True))
                                f.close()

    @classmethod
    def download_attachment(cls, gid=None, qid=None, msg_list=[]):
        # 搜索所有未读邮件
        retry_times = 5
        connected = False
        for retyr in range(retry_times):
            try:
                cls._messages = cls._email_server.search()
                connected = True
                break
            except:
                send_message(f'{cls._email_address}已断开连接，正在第{retyr+1}次重新连接', gid, qid)
                cls.connect_email(gid, qid, msg_list)
        if connected:
            processed_email_ids = ExperimentInfo.get_processed_email_ids()
            unprocessed_email_ids = [id for id in cls._messages if id not in processed_email_ids]
            cls.download_attachment_by_email_ids(unprocessed_email_ids, gid, qid)
            ExperimentInfo.note_processed_email_ids(unprocessed_email_ids)
        else:
            send_message(f'连接失败', gid, qid)
            cls._auto_download_stop = True

    @classmethod
    def auto_download_attachment(cls, gid=None, qid=None, msg_list=[]):
        flag = 'start'
        if msg_list:
            flag = msg_list[0]
        if flag == 'start' or flag == '开始':
            def auto_download_attachment_thread(gid, qid):
                send_message('自动下载已开始', gid, qid)
                last_check_time = -1
                while not cls._auto_download_stop:
                    if last_check_time < 0 or time.time() - last_check_time > 30:
                        last_check_time = time.time()
                        cls.download_attachment(gid, qid)
                    else:
                        time.sleep(1)
                send_message('自动下载已退出', gid, qid)
            cls._auto_download_thread = threading.Thread(target=auto_download_attachment_thread, args=(gid, qid,), name='auto_download')
            cls._auto_download_stop = False
            cls._auto_download_thread.start()
        elif flag == 'stop' or flag == '停止':
            cls._auto_download_stop = True
        
func_dict = {
    '#连接邮箱': {
        'func': EMailServer.connect_email,
        'permission': 'ROOT'
        },
    '#下载附件':{
        'func': EMailServer.download_attachment,
        'permission': 'ROOT'
        },
    '#自动下载':{
        'func': EMailServer.auto_download_attachment,
        'permission': 'ROOT'
        },
    }