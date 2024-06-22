import can
import subprocess
import json

config_file = open("code_rep/config.json")
config = json.load(config_file)

can_list = config["can_channel"]
bus_list = []
log_file_path = "log/log.txt"


class CallBackFunction(can.Listener):
    def on_message_received(self, msg: can.Message) -> None:
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
        print(can_info_str)
        log_file = open(log_file_path, "a")
        log_file.write(can_info_str + "\n")
        log_file.close()

    def stop(self) -> None:
        return super().stop()


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
msg = can.Message(arbitration_id=0x00041234, data=bytearray([12]))
# period = seconds
bus_list[0].send_periodic(msgs=msg, period=3)
try:
    while True:
        pass
except KeyboardInterrupt:
    print("exit")
    for i in bus_list:
        i.shutdown()
