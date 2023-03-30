import socket, numpy, json

server_ip, server_port = '10.0.20.21', 7001
vent_ip, vent_ip = '', 7005

# def to_temp(adc, r):
#     return round((adc / 1023.0) * 5 * 100, r)

def to_temp(adc, r):
    print(f'adc: {adc}')
    return round(numpy.interp(adc, [0, 1024], [-40, 125]), r)

def to_pwm(temp):
    print(f'input_temp: {temp}')
    if temp > 0:
        return int(numpy.interp(temp, [0, 18], [160, 255]))
    return 0

indoors, outdoors = 20, 20
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as vent:
        sock.bind((server_ip, server_port))
        sock.listen(server_port)
        while True:
            try:
                client, addr = sock.accept()
                # client.settimeout(6.0)
                print('[CLIENT_CONNECTED]')
                packet = client.recv(512)
                packet = packet.decode()
                print(f'Packet: {packet}')
                if packet[0] == 'i':
                    indoors = to_temp(int(packet[1:]), 2)
                    pwm = to_pwm(indoors - outdoors)
                    print(f'pwm: {pwm}')
                    data = {'pwm': pwm}
                    data['window'] = 1 if int(pwm) else 0
                    data_json = json.dumps(data)
                    print(f'data: {data_json}')
                    client.send(data_json.encode())
                else:
                    outdoors = to_temp(int(packet[1:]), 2)
                print(f'Indoors: {indoors}, Outdoors: {outdoors}')
                client.close()
            except Exception as e:
                print(e)
                client.close()
