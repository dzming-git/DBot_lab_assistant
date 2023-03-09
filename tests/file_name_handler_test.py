from DBot_SDK import ConfigFromUser
from conf.experiment_info import ExperimentInfo
from utils.file_name_handler import file_name_handler

def load_conf():
    ConfigFromUser.Authority_load_config('conf/authority/authority.yaml')
    ConfigFromUser.RouteInfo_load_config('conf/route_info/route_info.yaml')
    ExperimentInfo.load_config('conf/experiment_info/experiment_info.yaml')

if __name__ == '__main__': 
    load_conf()
    files = [
                '周二上午_5组_第1次实验.pdf', 
                '周2上午_五组_第1次实验.pdf', 
                '周2上午_五组_第一次实验.pdf']
    for file in files:
        print(file_name_handler(file))
