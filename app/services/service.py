import imapclient
import os
import email
import threading
import time
from dzmicro import send_message
from conf.experiment_info import ExperimentInfo
from utils import file_name_handler, subject_name_handler, decode_name

def help(task):
    from dzmicro import Authority
    authority = Authority()
    source_id = task.get('source_id', None)
    platform = task.get('platform', None)
    gid, qid = source_id
    permission_level = authority.get_permission_level(source_id)
    permission = authority.get_permission_by_level(permission_level)
    if gid:
        message = f'[CQ:at,qq={qid}]\n'
    message = f'关键词 {KEYWORD}\n当前权限 {permission}\n可调用指令如下\n'
    for command in list(func_dict.keys()):
        if authority.check_command_permission(command, source_id):
            message += f'  - {command}\n'
    send_message(message.strip(), source_id, platform)


class EMailServer:
    _email_server = None
    _email_address = ''
    _messages = []
    _auto_download_thread = None
    _auto_download_stop = True

    @classmethod
    def connect_email(cls, task):
        source_id = task.get('source_id', None)
        platform = task.get('platform', None)
        gid, qid = source_id
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
        send_message(f'登录{cls._email_address}成功', source_id, platform)
    
    @classmethod
    def download_attachment_by_email_id(cls, email_id, source_id, platform):
        output = f'{email_id}\n'
        for uid, message_data in cls._email_server.fetch(email_id, 'RFC822').items():
            email_message = email.message_from_bytes(message_data[b'RFC822'])
            email_subject = email_message['Subject']
            print(email_subject)
            for part in email_message.walk():
                # 如果是附件
                if part.get_content_disposition() == 'attachment':
                    filename = part.get_filename()
                    if filename:
                        decoded_filename = decode_name(filename)
                        decoded_subject = decode_name(email_subject)
                        output += f'    subject: {decoded_subject}'
                        try:
                            file_name_without_type, time_info, group_id, experiment_id = subject_name_handler(decoded_subject)
                            file_type = decoded_filename.split('.')[-1]
                        except:
                            try:
                                file_name_without_type, file_type, time_info, group_id, experiment_id = file_name_handler(decoded_subject)
                            except:
                                output += f'subject: {decoded_subject} file: {decoded_filename}未识别\n'
                                send_message(f'        {decoded_subject}\n未识别', source_id, platform)
                                continue
                        if file_name_without_type:
                            print(file_name_without_type)
                            folder_path = os.path.join(ExperimentInfo.get_save_path(), time_info, experiment_id)
                            filename = f'{file_name_without_type}.{file_type}'
                            file_path = os.path.join(folder_path, filename)
                            if os.path.exists(file_path):
                                index = 1
                                while True:
                                    filename = f'{file_name_without_type}_{index}.{file_type}'
                                    new_file_path = os.path.join(folder_path, filename)
                                    if not os.path.exists(new_file_path):
                                        file_path = new_file_path
                                        break
                                    index += 1
                            os.makedirs(folder_path, exist_ok=True)
                            output += f'        file: {filename}下载成功\n'
                            send_message(f'{filename}\n下载成功', source_id, platform)
                            # 下载附件
                            with open(file_path, 'wb') as f:
                                f.write(part.get_payload(decode=True))
                                f.close()
        return output

    @classmethod
    def download_attachment(cls, task):
        source_id = task.get('source_id', None)
        platform = task.get('platform', None)
        args = task.get('args', [])
        gid, qid = source_id
        # 搜索所有未读邮件
        retry_times = 5
        connected = False
        for retry in range(retry_times):
            try:
                cls._messages = cls._email_server.search()
                connected = True
                break
            except:
                send_message(f'{cls._email_address}已断开连接，正在第{retry+1}次重新连接', source_id, platform)
                cls.connect_email(task)
        if connected:
            processed_email_ids = ExperimentInfo.get_processed_email_ids()
            unprocessed_email_ids = [id for id in cls._messages if id not in processed_email_ids]
            for unprocessed_email_id in unprocessed_email_ids:
                output = cls.download_attachment_by_email_id(unprocessed_email_id, source_id, platform)
                ExperimentInfo.note_processed_email_ids(output)
        else:
            send_message(f'连接失败', gid, qid)
            cls._auto_download_stop = True

    @classmethod
    def auto_download_attachment(cls, task):
        source_id = task.get('source_id', None)
        platform = task.get('platform', None)
        args = task.get('args', [])
        gid, qid = source_id
        flag = 'start'
        if args:
            flag = args[0]
        if flag == 'start' or flag == '开始':
            def auto_download_attachment_thread(source_id, platform):
                send_message('自动下载已开始', source_id, platform)
                last_check_time = -1
                while not cls._auto_download_stop:
                    if last_check_time < 0 or time.time() - last_check_time > 30:
                        last_check_time = time.time()
                        cls.download_attachment(task)
                    else:
                        time.sleep(1)
                send_message('自动下载已退出', source_id, platform)
            cls._auto_download_thread = threading.Thread(target=auto_download_attachment_thread, args=(source_id, platform,), name='auto_download')
            cls._auto_download_stop = False
            cls._auto_download_thread.start()
        elif flag == 'stop' or flag == '停止':
            cls._auto_download_stop = True

KEYWORD = '#助教'
func_dict = {
    '帮助': {
        'func': help,
        'permission': 'USER'
        },
    '连接邮箱': {
        'func': EMailServer.connect_email,
        'permission': 'ROOT'
        },
    '下载附件':{
        'func': EMailServer.download_attachment,
        'permission': 'ROOT'
        },
    '自动下载':{
        'func': EMailServer.auto_download_attachment,
        'permission': 'ROOT'
        },
    }