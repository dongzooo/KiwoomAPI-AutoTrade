# 키움증권 API를 활용한 자동매매 프로그램

## 1. Abstract
- 사용자가 상시확인하는 것이 아닌 자동매매라는 목적, 따라서 UI 인터페이스는 없으면 커멘드 창에서 매매가 이루어짐
- 본 코드는 키움증권 모의투자 기준, 실투 시 로그인 메서드 변경

## 2. Request
- 키움증권API 
- 파이썬 32bit 

## 3. Function
- 매도시점, 매수시점 설정 후 자동매매
- 프로그램 시작후 30일동안의 저점을 잇는 지지선, 고점을 잇는 저항선 계산됌, 그 후 매매 시작
- 현재가격이 지지선에 도달하면 1주 매수, 저항선에 도달하면 1주 매도 


