# 소켓을 사용하기 위해서는 socket을 import해야 한다.	
import socket, threading
from module import detect, naverAPI
from cosinSimilarity import cosinSimilarity
import torch
import json
import time


# 학습모델 가져오기
model_path = torch.hub.load('ultralytics/yolov5', 'custom', path='weights\\final.pt')
 	
# binder함수는 서버에서 accept가 되면 생성되는 socket 인스턴스를 통해 client로 부터 데이터를 받으면 echo형태로 재송신하는 메소드이다.	
def binder(client_socket, addr):
  # 커넥션이 되면 접속 주소가 나온다.	
  print('Connected by', addr)
  ditectTargetDict = dict()
  try:
    # 접속 상태에서는 클라이언트로 부터 받을 데이터를 무한 대기한다.	
    # 만약 접속이 끊기게 된다면 except가 발생해서 접속이 끊기게 된다.	
    while True:	
      # socket의 recv함수는 연결된 소켓으로부터 데이터를 받을 대기하는 함수입니다. 최초 4바이트를 대기합니다.	
      sel = client_socket.recv(4)
      # 최초 4바이트는 전송할 데이터의 크기이다. 그 크기는 little big 엔디언으로 byte에서 int형식으로 변환한다.	
      # C#의 BitConverter는 big엔디언으로 처리된다.	
      selnum = int.from_bytes(sel, "little")
      if selnum == 1:
        print("===========================================================")
        print("이미지 받기")
        # socket의 recv함수는 연결된 소켓으로부터 데이터를 받을 대기하는 함수입니다. 최초 4바이트를 대기합니다.	
        data = client_socket.recv(4)
        # 최초 4바이트는 전송할 데이터의 크기이다. 그 크기는 little big 엔디언으로 byte에서 int형식으로 변환한다.	
        # C#의 BitConverter는 big엔디언으로 처리된다.	
        length = int.from_bytes(data, "little")
        # 다시 데이터를 수신한다.
        if length > 1024:
          data = client_socket.recv(1024)
          while (length - len(data)) > 0:
            data += client_socket.recv(length - len(data))
        else:
          data = client_socket.recv(length)
        
        # path = r"C:\WorkSpace\find_cloth\find_cloth_soket_server\images\target\target.jpeg"
        # detect.bytesToImagePath(data, path)
        ditectTargetDict = detect.exportModel(data, model_path)
        try:
            result = {
              "categories" : list(ditectTargetDict.keys())
            }
            result = json.dumps(result)
        except:
            print("No detected") #수정 필요
            
        msg = result
        # 바이너리(byte)형식으로 변환한다.
        senddata = msg.encode('utf-8')
        # 바이너리의 데이터 사이즈를 구한다.	
        length = len(msg)
        # 데이터 사이즈를 little 엔디언 형식으로 byte로 변환한 다음 전송한다.
        client_socket.sendall(length.to_bytes(4, byteorder='little'))
        # 데이터를 클라이언트로 전송한다.	
        client_socket.sendall(senddata)
        print("send: ", msg)
        print("===========================================================")
        
      elif selnum == 2:
        start = time.time()
        # socket의 recv함수는 연결된 소켓으로부터 데이터를 받을 대기하는 함수입니다. 최초 4바이트를 대기합니다.	
        data = client_socket.recv(4)
        # 최초 4바이트는 전송할 데이터의 크기이다. 그 크기는 little big 엔디언으로 byte에서 int형식으로 변환한다.	
        # C#의 BitConverter는 big엔디언으로 처리된다.	
        length = int.from_bytes(data, "little")
        # 다시 데이터를 수신한다.	
        data = client_socket.recv(length)
        # 수신된 데이터를 str형식으로 decode한다.	
        msg = data.decode()
        # 수신된 메시지를 콘솔에 출력한다.
        print("===========================================================")
        print("전송 받은 카테고리: ", msg)
        selectedClass = msg
        
        # 네이버쇼핑에서 검색 후 Product 리스트 생성
        products = naverAPI.searchNaverShop(selectedClass)
        
        # 검색된 품목에서 객체 탐지 후 선택 카테고리가 없으면 제거
        i = 0
        for x in range(len(products)):
          product = products[i]
          try:
              product.detected = detect.exportModel(product.imageBytes, model_path)
              product.detected[selectedClass]
              i = i + 1
          except:
            del products[i]
          finally:
            if i >= len(products):
              break
        
        # 유사도 비교 및 정렬
        compareDict = cosinSimilarity.compare(selectedClass, ditectTargetDict, products)
        sortedDict = dict(sorted(compareDict.items(), reverse=True))

        # 유사도 상위 10개 리스트 생성
        TopTenProducts= list()
        for i, row in enumerate(sortedDict.items()):
            if (i == 12): break
            similarity = row[0]
            product = row[1]
            TopTenProducts.append(
              {
                "similarity": similarity,
                "title" : product.title,
                "link" : product.link,
                "image" : product.image,
                "lprice" : product.lprice,
              }
            )
            
        # 유사도 리스트 JSON형식 생성
        result = {
          "products": TopTenProducts
        }
        print(result)
        # 딕셔너리를 JSON 문자열로 변경
        result = json.dumps(result) # ensure_ascii=false는 한글깨짐 방지

        # 비교 파일 제거
        del products
        del sortedDict
        del TopTenProducts
        
        
        # 바이너리(byte)형식으로 변환한다.	
        data = result.encode()
        # 바이너리의 데이터 사이즈를 구한다.	
        length = len(result)
        # 데이터 사이즈를 little 엔디언 형식으로 byte로 변환한 다음 전송한다.
        client_socket.sendall(length.to_bytes(4, byteorder='little'))
        # 데이터를 클라이언트로 전송한다.	
        client_socket.sendall(data) 
        print("time :", time.time() - start)  # 현재시각 - 시작시간 = 실행 시간 
        
      # 연결 종료 메세지 수신
      elif selnum == 3:
        data = client_socket.recv(4)	
        length = int.from_bytes(data, "little")
        data = client_socket.recv(length)	
        msg = data.decode()
        
        print(str(addr) + " " + msg)
        break
         
  except Exception as e:	
    print(e)
    # 접속이 끊기면 except가 발생한다.	
    print("except : " , addr)
  finally:	
    # 접속이 끊기면 socket 리소스를 닫는다.	
    client_socket.close()
 	
# 소켓을 만든다.	
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# 소켓 레벨과 데이터 형태를 설정한다.	
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# 서버는 복수 ip를 사용하는 pc의 경우는 ip를 지정하고 그렇지 않으면 None이 아닌 ''로 설정한다.	
# 포트는 pc내에서 비어있는 포트를 사용한다. cmd에서 netstat -an | find "LISTEN"으로 확인할 수 있다.	
server_socket.bind(('172.30.1.99', 5000))
print("listen")
# server 설정이 완료되면 listen를 시작한다.	
server_socket.listen()
 	
try:	
  # 서버는 여러 클라이언트를 상대하기 때문에 무한 루프를 사용한다.	
  while True:	
    # client로 접속이 발생하면 accept가 발생한다.	
    # 그럼 client 소켓과 addr(주소)를 튜플로 받는다.	
    client_socket, addr = server_socket.accept()
    th = threading.Thread(target=binder, args = (client_socket,addr))
    # 쓰레드를 이용해서 client 접속 대기를 만들고 다시 accept로 넘어가서 다른 client를 대기한다.	
    th.start()
except Exception as e:	
  print("server : " + e)
finally:	
   # 에러가 발생하면 서버 소켓을 닫는다.	
  server_socket.close()
