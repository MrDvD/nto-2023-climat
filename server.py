import socket, numpy, json

server_ip, server_port = '10.0.20.21', 7000
vent_ip, vent_ip = '', 7005

def to_temp(adc, r):
    return round((adc / 1023.0) * 5 * 100, r)

# def to_temp(adc, r):
#     return round(numpy.interp(adc, [0, 1024], [-45, 50]), r)

def to_pwm(temp):
    if temp > 16:
        return numpy.interp(temp, [16, 31], [0, 6000])
    return 0

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as vent:
        sock.bind((server_ip, server_port))
        sock.listen(server_port)
        while True:
            try:
                client, addr = sock.accept()
                print('[CLIENT_CONNECTED]')
                packet = client.recv(512)
                print(f'Packet: {packet}')
                if packet[0] == 'i':
                    indoors = to_temp(int(packet[1:]), 2)
                    pwm = to_pwm(indoors - outdoors)
                    print(pwm)
                    data = {'pwm': pwm}
                    data['window'] = 1 if int(pwm) else 0
                    data_json = json.dumps(data)
                    print(data_json)
                    client.send(data_json.encode())
                else:
                    outdoors = to_temp(int(packet[1:]), 2)
                print(f'Indoors: {indoors}, Outdoors: {outdoors}')
                client.close()
            except Exception as e:
                print(e)
                client.close()
