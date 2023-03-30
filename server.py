import socket, numpy, json, re

server_ip, server_port = '10.42.0.1', 7000
vent_ip, vent_ip = '', 7005

# def to_temp(adc, r):
#     return round((adc / 1023.0) * 5 * 100, r)

# def to_temp(adc, r):
#     print(f'adc: {adc}')
#     return round(numpy.interp(adc, [0, 1024], [-40, 125]), r)

def to_temp(adc, r):
    print(f'adc: {adc}')
    return round(adc / 10 - 273, r)

def to_pwm(temp_diff):
    print(f'temp_diff: {temp_diff}')
    if temp_diff > 0:
        return int(numpy.interp(temp_diff, [0, 10], [160, 255]))
    return 0

get_html = re.compile(r'^GET / ')
get_js = re.compile(r'^GET /script.js ')
get_css = re.compile(r'^GET /styles.css ')
get_info = re.compile(r'^GET /info ')
get_other = re.compile(r'^GET ')

with open('site/website.html', 'r') as html:
    with open('site/script.js', 'r') as js:
        with open('site/styles.css', 'r') as css:
            website = html.readlines()
            website = ''.join(website)
            script = js.readlines()
            script = ''.join(script)
            styles = css.readlines()
            styles = ''.join(styles)

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
                if get_html.match(packet):
                    header = f'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n{website}'
                    client.send(header.encode())
                    client.close()
                    continue
                elif get_js.match(packet):
                    header = f'HTTP/1.1 200 OK\r\nContent-Type: text/javascript\r\n\r\n{script}'
                    client.send(header.encode())
                    client.close()
                    continue
                elif get_css.match(packet):
                    header = f'HTTP/1.1 200 OK\r\nContent-Type: text/css\r\n\r\n{css}'
                    client.send(header.encode())
                    client.close()
                    continue
                elif get_info.match(packet):
                    info = {'outside': outside,
                            'inside': inside,
                            'difference': indoors - outdoors,
                            'fan': str(numpy.interp(pwm, [160, 255], [0, 100])) + '%',
                            'window': 'opened' if int(pwm) else 'closed'}
                    info = json.dumps(info)
                    header = f'HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n{info}'
                    client.send(header.encode())
                    client.close()
                    continue
                elif get_other.match(packet):
                    header = f'HTTP/1.1 404 Not Found\r\n\r\n'
                    client.send(header.encode())
                    client.close()
                    continue
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
