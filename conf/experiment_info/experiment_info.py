import yaml
from DBot_SDK import WatchDogThread

class ExperimentInfo:
    _config_path = ''
    _watch_dog = None
    _email_info = {}
    _pattern = ''
    _filename_format = ''
    _save_path = ''
    _processed_email_ids_path = ''

    @classmethod
    def load_config(cls, config_path, reload_flag=False):
        with open(config_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            cls._email_info = data.get('email', {})
            cls._pattern = data.get('pattern', '')
            cls._filename_format = data.get('filename_format', '')
            cls._save_path = data.get('save_path', '')
            cls._processed_email_ids_path = data.get('processed_email_ids_path', '')
            if not reload_flag:
                cls._config_path = config_path
                cls._watch_dog = WatchDogThread(config_path, cls.reload_config)
                cls._watch_dog.start()
    
    @classmethod
    def reload_config(cls):
        cls.load_config(config_path=cls._config_path, reload_flag=True)

    @classmethod
    def get_email_info(cls):
        return cls._email_info

    @classmethod
    def get_pattern(cls):
        return cls._pattern
    
    @classmethod
    def get_filename_format(cls):
        return cls._filename_format
    
    @classmethod
    def get_save_path(cls):
        return cls._save_path
    
    @classmethod
    def get_processed_email_ids_path(cls):
        return cls._processed_email_ids_path

    @classmethod
    def get_processed_email_ids(cls):
        processed_email_ids = []
        with open(cls._processed_email_ids_path, 'r', encoding='utf-8') as f:
            for line in f.readlines():
                try:
                    processed_email_ids = [int(line.strip())]
                except:
                    pass
            f.close()
        return processed_email_ids
    
    @classmethod
    def note_processed_email_ids(cls, ids):
        if type(ids) is not list:
            ids = [ids]
        processed_email_ids = cls.get_processed_email_ids()
        with open(cls._processed_email_ids_path, 'a', encoding='utf-8') as f:
            for id in ids:
                if id not in processed_email_ids:
                    f.write(f'{id}\n')
            f.close()
