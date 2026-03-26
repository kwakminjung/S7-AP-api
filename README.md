## How to Start
- git clone
```
git clone git@github.com:kwakminjung/S7-AP-api.git
```
- `.env` 파일 설정 (전달 예정 파일)
```
cp .env.example.env
vi .env
```
- 실행
```
~/S7-AP-api$ ./run.sh
```

## AP List API 명세

| index | method | URL | description |
| :---: | :---: | :--- | :--- |
| 1 | GET | `/aplist` | AP List에 있는 모든 AP의 Type, Name, IP, MAC, Map, Template, Status, # of Users, CAPWAP, AP Ver., Serial Number 조회 API |
| 2 | GET | `/aplist/{ap_name}` | AP의 Name (ap_name)을 통해 해당 AP의 Type, Name, IP, MAC, Map, Template, Status, # of Users, CAPWAP, AP Ver., Serial Number 조회 API |
| 3 | GET | `/aplist/{ap_name}/users` | AP에 접속한 devices 상태 조회 API |

## AP List API 동작 아키텍처
<img width="1398" height="854" alt="image" src="https://github.com/user-attachments/assets/3a01c108-d434-408c-9122-80d3b6db87bd" />
