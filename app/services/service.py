import imapclient
import os
import email
import chardet
from email.header import decode_header
from conf.experiment_info import ExperimentInfo
from utils import file_name_handler

class EMailServer:
    _email_server = None
    _messages = []

    @classmethod
    def connect_email(cls, gid=None, qid=None, msg_list=[]):
        message_parts = []
        if gid:
            message_parts.append(f'[CQ:at,qq={qid}]')
        # 获取邮箱信息
        email_info = ExperimentInfo.get_email_info()
        email_address = email_info.get('address', None)
        email_password = email_info.get('password', None)
        server_host = email_info.get('host', None)
        # 连接到IMAP服务器
        cls._email_server = imapclient.IMAPClient(server_host, ssl= True)
        cls._email_server.login(email_address, email_password)
        cls._email_server.id_({"name": "IMAPClient", "version": imapclient.version.version})
        info = cls._email_server.select_folder('INBOX', readonly = True)
        # 搜索所有未读邮件
        cls._messages = cls._email_server.search()
        message_parts.append(f'连接成功，共{len(cls._messages)}条邮件')
        # processed_email_ids = ExperimentInfo.get_processed_email_ids()
        
        message_send = '\n'.join(message_parts).rstrip('\n')
        return message_send
    
    @classmethod
    def download_attachment(cls, gid=None, qid=None, msg_list=[]):
        message_parts = []
        if gid:
            message_parts.append(f'[CQ:at,qq={qid}]')
        processed_email_ids = ExperimentInfo.get_processed_email_ids()
        unprocessed_email_ids = [id for id in cls._messages if id not in processed_email_ids]
        for id, message_data in cls._email_server.fetch(unprocessed_email_ids, 'RFC822').items():
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
                            message_parts.append(f'下载{decoded_filename}')
                            # 下载附件
                            with open(file_path, 'wb') as f:
                                f.write(part.get_payload(decode=True))
                                f.close()
        ExperimentInfo.note_processed_email_ids(unprocessed_email_ids)
        message_send = '\n'.join(message_parts).rstrip('\n')
        return message_send

func_dict = {
    '#连接邮箱': {
        'func': EMailServer.connect_email,
        'permission': 'ROOT'
        },
    '#下载附件':{
        'func': EMailServer.download_attachment,
        'permission': 'ROOT'
        }
    }