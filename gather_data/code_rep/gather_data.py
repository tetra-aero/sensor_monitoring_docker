import socketserver
import json

log_file_path = "log/log.txt"
log_output_health_path = "log/health_state"


def write_raw_can_data_to_file(can_info_str: str) -> None:
    with open(log_file_path, "a") as log_file:
        log_file.write(can_info_str + "\n")


def write_health_data_to_file(data: str) -> None:
    with open(log_output_health_path, "w") as log_output_health:
        log_output_health.write(data)


class TCPHandler(socketserver.BaseRequestHandler):

    def handle(self):
        # self.request is the TCP socket connected to the client
        maximum_data_size = 1024
        self.data = self.request.recv(maximum_data_size).strip()
        rec_str = self.data.decode("utf-8")
        rec_str_list = json.loads(rec_str)
        if rec_str_list[0] == "can_raw_data":
            write_raw_can_data_to_file(rec_str_list[1])
        elif rec_str_list[0] == "can_health_state":
            write_health_data_to_file(rec_str_list[1])
        else:
            print(f"unknown data recieved: {rec_str}")


if __name__ == "__main__":
    HOST, PORT = "172.20.10.5", 2222

    # Create the server
    server = socketserver.TCPServer((HOST, PORT), TCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
