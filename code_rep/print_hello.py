import can
import subprocess
can_list = ["can0"]
bus_list = []
class CallBackFunction(can.Listener):
    def on_message_received(self, msg):
#    print("hoge")
#    print(hex(msg.arbitration_id)
        print(msg)
        print("-----")
        print(msg.data)
        print("-----")
        print(msg.data.hex())
call_back_function = CallBackFunction()
for st in can_list:
    subprocess.run(["ip", "link", "set", "dev", st, "down"])
    subprocess.run(["ip", "link", "set", "dev", st, "type", "can", "bitrate", "125000"])
    subprocess.run(["ip", "link", "set", "dev", st, "up"])
    bus_tmp = can.interface.Bus(channel = st, bustype='socketcan', bitrate=125000, canfilters=None)
    bus_list.append(bus_tmp)
    can.Notifier(bus_tmp, [call_back_function, ])


bus0 = can.interface.Bus(channel = 'can0', bustype='socketcan', bitrate=125000, canfilters=None)

# コールバック関数登録

try:
    while True:
        pass
except KeyboardInterrupt:
    print('exit')
    bus0.shutdown()
