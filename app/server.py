# service.py
import time
from DBot_SDK import ConfigFromUser, server_thread
from app.services.service import func_dict, KEYWORD
from conf.experiment_info import ExperimentInfo
ConfigFromUser.Authority_load_config('conf/authority/authority.yaml')
ConfigFromUser.RouteInfo_load_config('conf/route_info/route_info.yaml')
ExperimentInfo.load_config('conf/experiment_info/experiment_info.yaml')
ConfigFromUser.set_func_dict(func_dict)
ConfigFromUser.set_keyword(KEYWORD)

from DBot_SDK import server_thread

if __name__ == '__main__': 
    server_thread.start()
    while True:
        time.sleep(10)
