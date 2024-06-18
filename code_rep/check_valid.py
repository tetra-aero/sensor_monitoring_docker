import json

json_file = open("data_type.json")
data_type = json.load(json_file)
last_received = dict()


def check_valid(id: str, data: str, timestamp: str):
    last_received[id] = {data, timestamp}
    header_len = 4
    if id[0:header_len] in data_type["check_validation"].keys():
        return bool(data_type["check_validation"][id[0:header_len]][data])


def get_gachacon_id(arbitration_id: str):
    l = len(arbitration_id)
    return int(arbitration_id[l - 2 : l])
