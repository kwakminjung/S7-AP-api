## How to Start
- git clone
```
git clone https://github.com/kwakminjung/S7-AP-api.git
```
- `.env` 파일 설정
```
cd S7-AP-api
cp .env.example.env
vi .env
```
- 실행 (local server)
```
docker compose up --build -d
```
- 배포 (Kubernetes cluster)
```
./deploy.sh v3.4 # docker image new version (현재: v3.4)
```
  
## API 명세
- prefix: `localhost:8001/ews`

| index | method | URL | description |
| :---: | :---: | :--- | :--- |
| 1 | GET | `/aplist` | AP List에 있는 모든 AP의 Type, Name, IP, MAC, Map, Template, Status, # of Users, CAPWAP, AP Ver., Serial Number 조회 API |
| 2 | GET | `/aplist/{ap_name}` | AP의 Name (ap_name)을 통해 해당 AP의 Type, Name, IP, MAC, Map, Template, Status, # of Users, CAPWAP, AP Ver., Serial Number 조회 API |
| 3 | GET | `/aplist/{ap_name}/users` | AP에 접속한 devices 상태 조회 API |
| 4 | GET | `/template` | AP List에서 현재 사용 중인 전체 template 정보 조회 API |
| 5 | GET | `/template/{template_num}` | template의 번호 (template_num)를 통해 해당 template의 radio, wlan_mode, channel_bandwidth, channel, tx_power, airtime_fairness, band_steering, basic_rate, ofdma, interference_detection, beacon_interval, minimum_signal_allowed, bss_coloring 정보 조회 API |

## API 아키텍처
<img width="1141" height="655" alt="image" src="https://github.com/user-attachments/assets/939b8715-79b6-4287-8a60-fd1122600dc6" />
