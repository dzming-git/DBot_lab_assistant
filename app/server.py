# service.py
from app import func_dict, KEYWORD
from dbot import DBot
from conf.experiment_info import ExperimentInfo

if __name__ == '__main__': 
    dbot = DBot()
    dbot.set_authority_config('conf/authority/authority.yaml')
    dbot.set_route_info_config('conf/route_info/route_info.yaml')
    dbot.set_consul_info_config('conf/consul_info/consul_info.yaml')
    ExperimentInfo.load_config('conf/experiment_info/experiment_info.yaml')
    dbot.set_keyword(KEYWORD)
    dbot.set_func_dict(func_dict)
    dbot.start()
