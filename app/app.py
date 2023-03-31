import socket, numpy, json, re, time, os

server_ip, server_port = '10.42.0.1', 7001

parse_payload = re.compile(r'\r\n\r\n(.+)')

hello_message = \
'List of commands:\n\
1) Set constants\n\
2) Monitor values\n\
3) Exit'

set_message = \
'List of commands:\n\
1) Lock Temperature Inside   6) Unlock Temperature Inside\n\
2) Lock Temperature Outside  7) Unlock Temperature Outside\n\
3) Lock Window State         8) Unlock Window State\n\
4) Lock Fan Duty             9) Unlock Fan Duty\n\
5) Back                     10) Set Desired Temperature'

get_info = 'GET /info HTTP/1.1\r\n\r\n'

def get_data():
   with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
      sock.connect((server_ip, server_port))
      sock.sendall(get_info.encode())
      info = sock.recv(512)
      info = info.decode()
      info = parse_payload.search(info)
      info = info.group(1)
      info = json.loads(info)
      outdoors = info['outdoors']
      indoors = info['indoors']
      difference = info['difference']
      fan = info['fan']
      window = info['window']
      desired = info['desired']
   return outdoors, indoors, difference, fan, window, desired

def get_cmd(arr):
   is_wrong = True
   while is_wrong:
      cmd = input('Type a number: ')
      if not cmd.isdigit() or int(cmd) not in arr:
         print('[ERROR] You entered a wrong command')
      else:
         return int(cmd)

def monitor_values():
   try:
      while True:
         os.system('clear')
         print('Climat State:')
         outdoors, indoors, difference, fan, window, desired = get_data()
         print(f'Temperature Outside: {outdoors}')
         print(f'Temperature Desired: {desired}')
         print(f'Temperature Inside: {indoors}')
         print(f'Temperature Difference (des-out): {difference}')
         print(f'Fan Duty: {fan}')
         print(f'Window State: {window}')
         print(f'[INFO] To exit, press "Ctrl+C"')
         time.sleep(1)
   except KeyboardInterrupt:
      return

def lock_val(text):
   os.system('clear')
   while True:
      val = input(f'Type a locked {text}: ')
      try:
         if text == 'Temperature':
            val = float(val)
         elif text == 'Fan Duty':
            val = int(val)
            if val not in list(range(101)):
               raise Exception
         elif text == 'Window State':
            val = int(val)
            if val not in [0, 1]:
               raise Exception
         return val
      except:
         os.system('clear')
         print(f'[ERROR] You entered a wrong {text}')
         continue

def set_constants():
      while True:
         try:
            os.system('clear')
            print(set_message)
            cmd = get_cmd([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
            if cmd == 10:
               os.system('clear')
               while True:
                   desired = input('Type a Desired Temperature: ')
                   try:
                       with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                           desired = int(desired)
                           header = f'POST /desired HTTP/1.1\r\n\r\n{desired}'
                           sock.connect((server_ip, server_port))
                           sock.send(header.encode())
                           os.system('clear')
                       break
                   except:
                       print('[ERROR] You entered a wrong Temperature')
                       continue
            elif cmd == 9:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    header = f'POST /unfan HTTP/1.1\r\n\r\n'
                    sock.connect((server_ip, server_port))
                    sock.send(header.encode())
            elif cmd == 8:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                   header = f'POST /unwindow HTTP/1.1\r\n\r\n'
                   sock.connect((server_ip, server_port))
                   sock.send(header.encode())
            elif cmd == 7:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                   header = f'POST /unoutdoors HTTP/1.1\r\n\r\n'
                   sock.connect((server_ip, server_port))
                   sock.send(header.encode())
            elif cmd == 6:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                   header = f'POST /unindoors HTTP/1.1\r\n\r\n'
                   sock.connect((server_ip, server_port))
                   sock.send(header.encode())
            elif cmd == 5:
               return
            elif cmd == 4:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                   pwm = int(lock_val('Fan Duty'))
                   header = f'POST /fan HTTP/1.1\r\n\r\n{pwm}'
                   sock.connect((server_ip, server_port))
                   sock.send(header.encode())
            elif cmd == 3:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                   window = int(lock_val('Window State'))
                   header = f'POST /window HTTP/1.1\r\n\r\n{window}'
                   sock.connect((server_ip, server_port))
                   sock.send(header.encode())
            elif cmd == 2:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                   outdoors = float(lock_val('Temperature'))
                   header = f'POST /outdoors HTTP/1.1\r\n\r\n{outdoors}'
                   sock.connect((server_ip, server_port))
                   sock.send(header.encode())
            elif cmd == 1:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                   indoors = float(lock_val('Temperature'))
                   header = f'POST /indoors HTTP/1.1\r\n\r\n{indoors}'
                   sock.connect((server_ip, server_port))
                   sock.send(header.encode())
         except Exception as e:
            os.system('clear')
            print(e)
            print('[ERROR] Selected action wasn\'t completed')
            continue

while True:
   os.system('clear')
   print(hello_message)
   cmd = get_cmd([1, 2, 3])
   if cmd == 3:
      os.system('clear')
      exit()
   if cmd == 2:
      monitor_values()
   if cmd == 1:
      set_constants()