## 키움증권 API를 활용한 자동매매 프로그램

### 1. Overview
- 사용자가 상시확인하는 것이 아닌 자동매매라는 목적, 따라서 UI는 없으며 cmd 창에서 매매가 이루어짐
- 본 코드는 키움증권 모의투자 기준, 실투 시 로그인 메서드 변경



### 2. Function
- 매도시점, 매수시점 설정 후 자동매매
- 원하는 종목은 리스트에 담아두어 저장
- 현 코드는 프로그램 시작 후 일정시간동안의 저점을 잇는 지지선, 고점을 잇는 저항선 계산됌, 그 후 매매 시작
- 현재가격이 지지선에 도달하면 1주 매수, 저항선에 도달하면 1주 매도 

### 3. Demo Video 
- 자동매매의 목적은 UI없이 다른 업무를 할 때도 돈을 벌고하는 목적임으로 UI없이 콘솔창에서 진행
- 매매결과는 콘솔창 혹은 영웅문 어플에서 확인가능
- 시연 영상



https://user-images.githubusercontent.com/40832965/154905620-34a5ff2d-d85c-46f3-8429-62cb20a71969.mp4



### 4. Requirements
- 키움증권API 발급 & 키움 Open API 프로그램 다운로드 링크 <br>
   https://www.kiwoom.com/h/customer/download/VOpenApiInfoView
- 파이썬 32bit 다운로드 *필수
- Pycharm
