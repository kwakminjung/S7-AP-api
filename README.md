## How to Start
- git clone
```
git clone [git@github.com:kwakminjung/S7-AP-api.git](https://github.com/kwakminjung/S7-AP-api.git)
```
- `.env` 파일 설정
```
cd S7-AP-api
cp .env.example.env
vi .env
```
- 실행
```
docker compose up --build -d
```
  
## AP List API 명세
- prefix: `localhost:8001/ews`

| index | method | URL | description |
| :---: | :---: | :--- | :--- |
| 1 | GET | `/aplist` | AP List에 있는 모든 AP의 Type, Name, IP, MAC, Map, Template, Status, # of Users, CAPWAP, AP Ver., Serial Number 조회 API |
| 2 | GET | `/aplist/{ap_name}` | AP의 Name (ap_name)을 통해 해당 AP의 Type, Name, IP, MAC, Map, Template, Status, # of Users, CAPWAP, AP Ver., Serial Number 조회 API |
| 3 | GET | `/aplist/{ap_name}/users` | AP에 접속한 devices 상태 조회 API |
| 4 | GET | `/aplist/{ap_name}/template` | AP의 template을 이용하여 radio, wlan_mode, channel_bandwidth, channel, tx_power, airtime_fairness, band_steering, basic_rate, ofdma, interference_detection, beacon_interval, minimum_signal_allowed, bss_coloring 정보 조회 API |

## AP List API 동작 아키텍처
<img width="1480" height="953" alt="image" src="https://github.com/user-attachments/assets/0e24d0df-949d-4e9d-ad45-0cc66c131b18" />

