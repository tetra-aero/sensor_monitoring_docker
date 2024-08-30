import can
import subprocess
import json
import time
import socket
import queue

# load config file
config = dict()
with open("code_rep/config.json") as config_file:
    config = json.load(config_file)

can_list = config["can_channel"]
bus_list = []
log_file_path = "log/log.txt"
log_output_health_path = "log/health_state"

# todo: move config to a place witch both recieve_can and gather_data can view
host, port = config["tcp_ip_info"]["host"], int(config["tcp_ip_info"]["port"])
maximum_data_size = 8192
can_data_que = queue.Queue()

# seconds
can_send_period = 0.5
check_can_received = 1
# last health checked timestamp
last_health_check = dict()
for header in config["check_validation"].keys():
    last_health_check[header] = dict()
for header in config["check_data_recieved"]:
    last_health_check[header] = dict()
    # store [timestamp, bool]

timestamp_on_start = time.time()


# recieve arbitration_id turned into hex str, call by f(hex(arbitration_id))
def get_header(arbitration_id: str) -> str:
    return arbitration_id[0 : len(arbitration_id) - 2]


def get_tail(arbitration_id: str) -> str:
    l = len(arbitration_id)
    return arbitration_id[l - 2 : l]


def get_gachacon_id(arbitration_id: str) -> int:
    return int(get_tail(arbitration_id))


def atemp_connection_tcp() -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        # Connect to server
        try:
            sock.connect((host, port))
            return True
        except:
            return False


def send_data_through_tcp(data_type: str, data) -> None:
    # may raise ConnectionRefusedError
    sending_data_dict = dict()
    sending_data_dict["data_type"] = data_type
    sending_data_dict["data"] = data
    sending_data = json.dumps(sending_data_dict)
    data_size = len(bytes(sending_data, "utf-8"))
    if data_size > maximum_data_size:
        print("data_size: ", data_size)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        # Connect to server and send data
        sock.connect((host, port))
        sock.sendall(bytes(sending_data, "utf-8"))


def send_data_in_queue(data_type: str, data_queue: queue.Queue) -> None:
    try_times = 0
    max_try_times = 3
    while not can_data_que.empty():
        try:
            send_data_through_tcp(data_type, data_queue.get())
        except:
            try_times += 1
            if not try_times < max_try_times:
                break


class CallBackFunction(can.Listener):
    def on_message_received(self, msg: can.Message) -> None:
        # data format for stdout and log
        id_str = hex(msg.arbitration_id)
        id_str = id_str.replace("0x", "")
        id_str = "0" * (8 - len(id_str)) + id_str
        can_info_str = (
            "("
            + str("{:.6f}".format(msg.timestamp, 6))
            + ")"
            + " "
            + str(msg.channel)
            + " "
            + id_str
            + "#"
            + msg.data.hex()
        )
        # send data to stdout
        # print(can_info_str)
        # send data via tcp
        try:
            send_data_through_tcp("can_raw_data", can_info_str)
        except:
            print("faild to send data")
            can_data_que.put(can_info_str)

        # store data in log
        with open(log_file_path, "a") as log_file:
            log_file.write(can_info_str + "\n")

        # check if information for health chk
        check_helth_list = config["check_validation"]
        check_data_recieved = config["check_data_recieved"]
        id_header = get_header(hex(msg.arbitration_id))
        if id_header in check_helth_list.keys() or id_header in check_data_recieved:
            gachacon_id = get_gachacon_id(hex(msg.arbitration_id))
            last_health_check[id_header][gachacon_id] = [time.time(), msg.data.hex()]

    def stop(self) -> None:
        return super().stop()


send_check_range = config["range"]
msgs = []
for i in range(send_check_range["start"], send_check_range["end"]):
    id_tail = hex(i)[2:]
    id_tail = "0" * (2 - len(id_tail)) + id_tail
    id = config["send_check_valid"]["head"] + id_tail
    msgs.append(
        can.Message(
            arbitration_id=int(id, 16),
            data=bytearray([int(config["send_check_valid"]["data"], 16)]),
        )
    )
call_back_function = CallBackFunction()
for st in can_list:
    subprocess.run(["ip", "link", "set", "dev", st, "down"])
    subprocess.run(["ip", "link", "set", "dev", st, "type", "can", "bitrate", "125000"])
    subprocess.run(["ip", "link", "set", "dev", st, "up"])
    bus_tmp = can.interface.Bus(
        channel=st, bustype="socketcan", bitrate=125000, canfilters=None
    )
    bus_list.append(bus_tmp)
    can.Notifier(
        bus_tmp,
        [
            call_back_function,
        ],
    )
    for msg in msgs:
        time.sleep(check_can_received * 0.01)
        bus_tmp.send_periodic(msgs=msg, period=can_send_period)
try:
    while True:
        time.sleep(check_can_received)
        check_valid_list = config["check_validation"]
        check_data_recieved = config["check_data_recieved"]
        iter_list = list(check_valid_list.keys()) + check_data_recieved
        st = config["range"]["start"]
        end = config["range"]["end"]
        output_health_state = dict()
        output_health_state["timestamp"] = time.time()
        # the health state flag does not correctly show the state
        for gachacon_id in range(st, end):
            output_health_state[str(gachacon_id)] = dict()
            health_flag = True
            for id_header in iter_list:
                output_health_state[str(gachacon_id)][id_header] = dict()
                if gachacon_id not in last_health_check[id_header].keys():
                    output_health_state[str(gachacon_id)][id_header][
                        "registered"
                    ] = False
                    if id_header in check_valid_list:
                        health_flag = False
                        continue
                    else:
                        continue

                else:
                    output_health_state[str(gachacon_id)][id_header][
                        "registered"
                    ] = True
                health_state = last_health_check[id_header][gachacon_id]
                output_health_state[str(gachacon_id)][id_header]["timestamp"] = (
                    health_state[0]
                )
                output_health_state[str(gachacon_id)][id_header]["data"] = health_state[
                    1
                ]

                if not (
                    abs(health_state[0] - output_health_state["timestamp"])
                    < check_can_received
                    and (
                        id_header not in check_valid_list
                        or health_state[1] == check_valid_list[id_header]["True"]
                    )
                ):
                    print(
                        "time: ",
                        abs(health_state[0] - output_health_state["timestamp"]),
                    )
                    print(
                        "id_header not in check_valid_list",
                        id_header not in check_valid_list,
                    )
                    print(
                        'health_state[1] == check_valid_list[id_header]["True"]: ',
                        health_state[1] == check_valid_list[id_header]["True"],
                    )

                    health_flag = False
                    print(
                        f"({output_health_state["timestamp"]}) unsufficient health state for header: {id_header}, gachacon_id: {gachacon_id}, last timestamp:{health_state[0]}, recieved health_state:{health_state[1]}"
                    )
            output_health_state[str(gachacon_id)]["health_state"] = health_flag

        with open(log_output_health_path, "w") as log_output_health:
            json.dump(output_health_state, log_output_health, indent=4)
        try:
            send_data_through_tcp("can_health_state", output_health_state)
        except:
            print("failed to send health data")

        if (not can_data_que.empty()) and atemp_connection_tcp():
            send_data_in_queue("can_raw_data", can_data_que)


finally:
    print("exit")
    for i in bus_list:
        i.shutdown()
