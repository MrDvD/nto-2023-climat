import socket, numpy, json, re

server_ip, server_port = '10.42.0.1', 7001
desired = 24
lock_indoors, lock_outdoors, lock_window, lock_fan = False, False, False, False

# def to_temp(adc, r):
#     return round((adc / 1023.0) * 5 * 100, r)

# def to_temp(adc, r):
#     print(f'adc: {adc}')
#     return round(numpy.interp(adc, [0, 1024], [-40, 125]), r)

def to_temp(adc, r):
    print(f'adc: {adc}')
    return round(adc / 1023 * 3.3 * 1000 / 10 - 273, r)

def to_pwm(temp_diff):
    print(f'temp_diff: {temp_diff}')
    if isinstance(temp_diff, str):
        return 0
    if temp_diff > 0:
        return int(numpy.interp(temp_diff, [0, 10], [160, 255]))
    return 0

# GET REQUESTS
get_html = re.compile(r'^GET / ')
get_js = re.compile(r'^GET /script.js ')
get_css = re.compile(r'^GET /styles.css ')
get_info = re.compile(r'^GET /info ')
get_other = re.compile(r'^GET ')
# POST REQUESTS
post_indoors = re.compile(r'POST /indoors ')
post_outdoors = re.compile(r'POST /outdoors ')
post_window = re.compile(r'POST /window ')
post_fan = re.compile(r'POST /fan ')
post_unindoors = re.compile(r'POST /unindoors ')
post_unoutdoors = re.compile(r'POST /unoutdoors ')
post_unwindow = re.compile(r'POST /unwindow ')
post_unfan = re.compile(r'POST /unfan ')
post_desired = re.compile(r'POST /desired ')
# PARSE REGEXPS
parse_payload = re.compile(r'\r\n\r\n(.+)')

with open('site/website.html', 'r') as html:
    with open('site/script.js', 'r') as js:
        with open('site/styles.css', 'r') as css:
            website = html.readlines()
            website = ''.join(website)
            script = js.readlines()
            script = ''.join(script)
            styles = css.readlines()
            styles = ''.join(styles)

indoors, outdoors, window_prev, window_curr, pwm_percent, pwm = '???', '???', '???', '???', '???', '???'
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
   sock.bind((server_ip, server_port))
   sock.listen(server_port)
   while True:
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
               info = {'outdoors': outdoors,
                       'indoors': indoors,
                       'difference': outdoors - desired if not isinstance(indoors, str) and not isinstance(outdoors, str) else 0,
                       'fan': str(numpy.interp(pwm if not isinstance(pwm, str) else 0, [160, 255], [0, 100])) + '%'}
               print(f'pwm: {pwm}')
               if lock_window:
                   if not isinstance(window_prev, str):
                       win_state = int(window_prev)
                   else:
                       win_state = 0
               else:
                   if not isinstance(window_curr, str):
                       win_state = int(window_curr)
                   else:
                       win_state = 0
               info['window'] = 'opened' if win_state else 'closed'
               info['desired'] = desired
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
            elif post_indoors.match(packet):
               indoors = parse_payload.search(packet)
               indoors = float(indoors.group(1))
               lock_indoors = True
               client.close()
               continue
            elif post_outdoors.match(packet):
               outdoors = parse_payload.search(packet)
               outdoors = float(outdoors.group(1))
               lock_outdoors = True
               client.close()
               continue
            elif post_window.match(packet):
               window_prev = parse_payload.search(packet)
               window_prev = int(window_prev.group(1))
               lock_window = True
               client.close()
               continue
            elif post_fan.match(packet):
               pwm_percent = parse_payload.search(packet)
               pwm_percent = int(pwm_percent.group(1))
               pwm = numpy.interp(pwm_percent, [0, 100], [160, 255])
               if pwm_percent == 0:
                   pwm = 0
               lock_fan = True
               client.close()
               continue
            elif post_unindoors.match(packet):
               lock_indoors = False
               client.close()
               continue
            elif post_unoutdoors.match(packet):
               lock_outdoors = False
               client.close()
               continue
            elif post_unwindow.match(packet):
               lock_window = False
               client.close()
               continue
            elif post_unfan.match(packet):
               lock_fan = False
               client.close()
               continue
            elif post_desired.match(packet):
               desired = parse_payload.search(packet)
               desired = int(desired.group(1))
               client.close()
               continue
            print(f'Packet: {packet}')
            if packet[0] == 'i':
               indoors = to_temp(int(packet[1:]), 2) if not lock_indoors else indoors
               if not isinstance(indoors, str) and not isinstance(outdoors, str):
                  pwm = to_pwm(outdoors - desired) if not lock_fan else pwm
               else:
                  pwm = 0 if not lock_fan else pwm
               print(f'pwm: {pwm}')
               data = {'pwm': pwm}
               
               window_curr = 1 if indoors - outdoors >= 0 and indoors > desired else 0
               if lock_window:
                  data['window'] = window_prev
               else:
                  data['window'] = window_curr
                  window_prev = window_curr
               data_json = json.dumps(data)
               print(f'data: {data_json}')
               client.send(data_json.encode())
            else:
               outdoors = to_temp(int(packet[1:]), 2) if not lock_outdoors else outdoors
            print(f'Indoors: {indoors}, Outdoors: {outdoors}')
            client.close()