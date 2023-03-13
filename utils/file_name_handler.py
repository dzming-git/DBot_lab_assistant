import re
from conf.experiment_info import ExperimentInfo
from cn2an import cn2an, an2cn

def pad_zero(match):
    num_str = match.group(0)
    if len(num_str) == 1:
        return "0" + num_str
    else:
        return num_str

def connector2underline(file_name):
    connectors = [' ', '+', '-', '——', '—']
    for connector in connectors:
        file_name = file_name.replace(connector, '_')
    return file_name

def chinese_to_arabic(text):
    # 定义正则表达式提取汉字数字
    chinese_num_pattern = re.compile(r'[一二三四五六七八九十百千万亿]+')
    # 提取字符串中的汉字数字
    chinese_nums = chinese_num_pattern.findall(text)
    # 遍历汉字数字，使用cn2an将其转换为阿拉伯数字
    for chinese_num in chinese_nums:
        arabic_num = str(cn2an(chinese_num, 'smart'))
        # 将转换后的阿拉伯数字替换原来的汉字数字
        text = text.replace(chinese_num, arabic_num)
    return text

def file_name_handler(file_name: str):
    # 统一连词符
    file_name = connector2underline(file_name)
    # 统一中文数字与阿拉伯数字
    file_name_without_type, file_type = file_name.split('.')
    time_str, group_id_str, experiment_id_str = file_name_without_type.split('_')
    weekdays = ["", "一", "二", "三", "四", "五", "六", "日"]
    time_str = re.sub(r"周(\d)", lambda m: "周" + weekdays[int(m.group(1))], time_str)
    group_id_str = chinese_to_arabic(group_id_str)
    experiment_id_str = chinese_to_arabic(experiment_id_str)
    file_name = f'{time_str}_{group_id_str}_{experiment_id_str}.{file_type}'
    # 拓展0
    file_name = re.sub(r'\d+', lambda x: '{:0>2d}'.format(int(x.group())), file_name)
    # 提取信息
    patterns = ExperimentInfo.get_pattern()
    for pattern in patterns:
        match = re.search(pattern, file_name)

        if match:
            time_info = match.group(1)
            group_id = match.group(2)
            experiment_id = match.group(3)
            file_name_without_type = ExperimentInfo.get_filename_format().format(time_info, group_id, experiment_id)
            return file_name_without_type, file_type, time_info, group_id, experiment_id
    return None, None, None, None, None