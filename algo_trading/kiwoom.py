import os
import time
import sys

from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from config.errorCode import *
from PyQt5.QtTest import *
from config.kiwoomType import *


class Kiwoom(QAxWidget):
    def __init__(self):
        super().__init__()

        self.readType = RealType()
        print("Kiwoom class 입니다.")

        ###event_loop 모음
        self.login_event_loop = None
        self.detail_account_info_event_loop = QEventLoop()
        self.calculator_event_loop = QEventLoop()
        self.calculator_event_loop2 = QEventLoop()

        ###스크린 번호 모음
        self.screen_start_stop_real = "1000"
        self.screen_info = "2000"
        self.screen_calculation_stock = "4000"
        self.screen_real_stock = "5000"  # 종목별로 할당할 스크린 번호
        self.screen_meme_stock = "6000"  # 종목별 할당할 주문용 스크린 번호

        ###변수모음
        self.account_num = None
        #기울기 변수
        self.stock_count = 0
        self.inclination_above1 = 0
        self.inclination_below1 = 0
        self.intercept_above1 = 0
        self.intercept_below1 = 0

        self.inclination_above2 = 0
        self.inclination_below2 = 0
        self.intercept_above2 = 0
        self.intercept_below2 = 0


        ###딕셔너리 모음
        self.account_stock_dict = {}  
        self.outstanding_share_dict = {}
        self.portfolio_stock_dict = {}
        self.jango_dict = {}

        ###종목 분석용
        self.calcul_data = []
        self.calcul_data_m = []

        ###계좌관련 변수
        self.use_money = 0
        self.use_money_percent = 0.5

        ###함수 모음
        self.get_ocx_instance()
        self.event_slots()
        self.real_event_slot()
        self.signal_login_commConnect()
        self.get_account_info()
        self.detail_account_info()  # 예수금 가져오는 것
        self.detail_account_mystock()  # 계좌평가 잔고내역 요청
        self.outstanding_share()  # 미체결종목

        #self.calculator_fnc() #종목분석용, 임시위치
        self.calculator_fnc2() # 분봉 종목분석용, 임시위치


        self.read_code()  # 저장된 종목들 불러온다.
        self.screen_number_setting()  # 스크린 번호를 할당한다.

        # 실시간 데이터
        # 마지막에 "0"은 장 운영구분을 받을 때만 0을 입력하고 나머지 실시간 데이터는 "1"을 입력한다.
        self.dynamicCall("SetRealReg(QString,QString,QString,QString)", self.screen_start_stop_real, '',
                         self.readType.REALTYPE['장시작시간']['장운영구분'],
                         "0")  # 장시작 시간인가 혹은 장 끝인가를 알기위함/#중간의 공백은 '' 장시간 파악임을 뜻함

        for code in self.portfolio_stock_dict.keys():
            screen_num = self.portfolio_stock_dict[code]['스크린번호']
            fids = self.readType.REALTYPE['주식체결']['체결시간']  # fid 번호 불러오기
            self.dynamicCall("SetRealReg(QString,QString,QString,QString)", screen_num, code, fids,
                             "1")  # 채결시단 fid넘버 =fids, 추가 정보를 알긴위해선 "1"
            print("실시간 등록 코드 : %s, 스크린 번호 : %s, fid번호 : %s" % (code, screen_num, fids))

       # self.day_kiwoom_db2()

    def get_ocx_instance(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")  # 응용프로그램을 제어하게 해준다.

    def event_slots(self):
        self.OnEventConnect.connect(self.login_slot)  # 임의로 마는 slot 값에다 넣어준다.0이 떠야 로그인 성공

    def real_event_slot(self):
        self.OnReceiveRealData.connect(self.realdata_slot)
        self.OnReceiveChejanData.connect(self.chejan_slot)  # 주문관련 슬롯
        self.OnReceiveMsg.connect(self.msg_slot)

    def login_slot(self, errCode):
        print(errors(errCode))
        self.login_event_loop.exit()
        self.OnReceiveTrData.connect(self.trdata_slot)


    def signal_login_commConnect(self):
        self.dynamicCall("CommConnect()")

        self.login_event_loop = QEventLoop()
        self.login_event_loop.exec_()

    def get_account_info(self):
        account_list = self.dynamicCall("GetLoginInfo(String)", "ACCNO")

        self.account_num = account_list.split(';')[0]

        print("나의 보유 계좌 번호 %s" % self.account_num)

    def detail_account_info(self):
        print("---예수금을 요청하는 부분---")
        # KOA tr조회 함수로 요청
        self.dynamicCall("SetInputValue(String, String)", "계좌번호", self.account_num)
        self.dynamicCall("SetInputValue(String, String)", "비밀번호", "0000")
        self.dynamicCall("SetInputValue(String, String)", "비밀번호입력매채구분", "00")
        self.dynamicCall("SetInputValue(String, String)", "조회구분", "2")
        self.dynamicCall("CommRqData(String, String, int, String)", "예수금상세현황요청", "opw00001", "0",
                         self.screen_info)  # 요청이름, tr번호, prenext, 화면번호

        self.detail_account_info_event_loop = QEventLoop()
        self.detail_account_info_event_loop.exec_()

    def detail_account_mystock(self, sPrevNext="0"):
        print("---계좌평가 잔고내역 요청 page%s---" % sPrevNext)
        self.dynamicCall("SetInputValue(String, String)", "계좌번호", self.account_num)
        self.dynamicCall("SetInputValue(String, String)", "비밀번호", "0000")
        self.dynamicCall("SetInputValue(String, String)", "비밀번호입력매채구분", "00")
        self.dynamicCall("SetInputValue(String, String)", "조회구분", "2")
        self.dynamicCall("CommRqData(String, String, int, String)", "계좌평가잔고내역요청", "opw00018", sPrevNext,
                         self.screen_info)  # 요청이름, tr번호, prenext, 화면번호

        self.detail_account_info_event_loop.exec_()

    def outstanding_share(self, sPrevNext="0"):
        print("---미체결요청---")
        self.dynamicCall("SetInputValue(String, String)", "계좌번호", self.account_num)
        self.dynamicCall("SetInputValue(String, String)", "체결구분", "1")
        self.dynamicCall("SetInputValue(String, String)", "매매구분", "0")
        self.dynamicCall("CommRqData(QString, QString, int, QString)", "실시간미체결요청", "opt10075", sPrevNext,
                         self.screen_info)  # 요청이름, tr번호, prenext, 화면번호

        self.detail_account_info_event_loop.exec_()

    def trdata_slot(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext):
        '''
        tr 요청을 받는  구역이다! 슬롯이다!
        :param sScrNo:  스크린번호
        :param sRQName:  내가 요청시 지은 이름
        :param sTrCode:  요청 id, tr코드
        :param sRecordName: 사용안함 레코드 이름
        :param sPrevNext:  다음페이지가 있는지 : 주식종목이 20개 이상이다 //다음페이지가 없으면 0, 있으면 2
        :return:
        '''

        if sRQName == "예수금상세현황요청":
            deposit = self.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, 0, "예수금")
            print("예수금 %s" % int(deposit))  # 00000123 -> 123 int로 스트림 갑싸기

            self.use_money = int(deposit) * self.use_money_percent
            self.use_money = self.use_money / 4

            ok_deposit = self.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, 0, "출금가능금액")
            print("출금가늠금액 %s" % int(ok_deposit))

            self.detail_account_info_event_loop.exit()

        if sRQName == "계좌평가잔고내역요청":
            total_buy_money = self.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, 0, "총매입금액")
            total_buy_money_result = int(total_buy_money)
            print("총 매입금액 %s" % total_buy_money_result)

            total_profit_loss_rate = self.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, 0,
                                                      "총수익률(%)")
            total_profit_loss_rate_result = float(total_profit_loss_rate)
            print("총수익률(%%) %s" % total_profit_loss_rate_result)  # %%두개 넣기

            rows = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)  # GetRepeatCnt API멀티데이터 불러옴
            cnt = 0  # 종목 개수를 파악하기 위한 변수 카운트

            for i in range(rows):
                code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목번호")
                code = code.strip()[1:]

                code_nm = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목명")
                stock_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                                  "보유수량")

                buy_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "매입가")
                learn_rate = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "수익률(%)")
                current_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "현재가")
                total_chegual_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName,i, "매입금액")
                possible_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"매매가능수량")

                if code in self.account_stock_dict:
                    pass
                else:
                    self.account_stock_dict.update({code: {}})  # =self.account_stock_dict[code] ={}

                code_nm = code_nm.strip()
                stock_quantity = int(stock_quantity.strip())
                buy_price = int(buy_price.strip())
                learn_rate = float(learn_rate.strip())  # 수익률은 소수점이 있어서  float이다.
                current_price = int(current_price.strip())
                total_chegual_price = int(total_chegual_price.strip())
                possible_quantity = int(possible_quantity.strip())

                # dynamicCall 한것들 딕셔너리에 저장
                asd = self.account_stock_dict[code]
                asd.update({"종목명": code_nm})
                asd.update({"보유수량": stock_quantity})
                asd.update({"매입가": buy_price})
                asd.update({"수익률(%)": learn_rate})
                asd.update({"현재가": current_price})
                asd.update({"매입금액": total_chegual_price})
                asd.update({"매매가능수량": possible_quantity})

                cnt += 1

            print("계좌에 가지고 있는 종목 %s" % self.account_stock_dict)
            print("보유 종목수 %s" % cnt)

            if sPrevNext == "2":
                self.detail_account_mystock(sPrevNext="2")
            else:
                self.detail_account_info_event_loop.exit()

        elif sRQName == "실시간미체결요청":

            rows = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)  # GetRepeatCnt API멀티데이터 불러옴

            for i in range(rows):
                code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목코드")
                code_nm = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목명")
                order_num = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문번호")
                order_status = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                                "주문상태")
                order_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                                  "주문수량")
                order_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                               "주문가격")
                order_gubun = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                               "주문구분")
                not_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                                "미체결수량")
                ok_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                               "체결량")

                code = code.strip()
                code_nm = code_nm.strip()
                order_num = int(order_num)
                order_status = order_status.strip()
                order_quantity = int(order_quantity)
                order_price = int(order_price)
                order_gubun = order_gubun.strip().lstrip('+').lstrip('-')
                not_quantity = int(not_quantity)
                ok_quantity = int(ok_quantity)

                if order_num in self.outstanding_share_dict:
                    pass
                else:
                    self.outstanding_share_dict[order_num] = {}

                osd = self.outstanding_share_dict[order_num]

                osd.update({"종목코드": code})
                osd.update({"종목명": code_nm})
                osd.update({"주문번호": order_num})
                osd.update({"주문상태": order_status})
                osd.update({"주문수량": order_quantity})
                osd.update({"주문가격": order_price})
                osd.update({"주문구분": order_gubun})
                osd.update({"미체결수량": not_quantity})
                osd.update({"체결량": ok_quantity})

                print("미쳬결 종목 : %s" % self.outstanding_share_dict[order_num])

            self.detail_account_info_event_loop.exit()

        elif sRQName == "주식일봉차트조회":
            code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "종목코드")
            code = code.strip()  # 불러온 데이터는 strip를 통해 여백을 없앤다.
            print("%s 일봉데이터 요청" % code) # 종목번호

            cnt = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)  # GetRepeatCnt API멀티데이터 불러옴
            print("데이터 일수 %s" % cnt) #데이터 받아온 일수

            # 한번 조회하면 600일치까지 일봉데이터를 받을 수 있다.
            # data = self.dynamicCall("getCommDataEx(QSting, QString)", strCode, sRQName)
            # 아래는 데이터의 형태
            # [["", "현재가", "거래량", "거래대금", "날짜", "시가", "고가", "저가", ""], ["","현재가","거래량","거래대금","날짜","시가","고가","저가",""]]
            #  0      1        2        3       4      5      6      7
            for i in range(cnt):
                data = []
                current_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"현재가")
                value = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "거래량")
                trading_value = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "거래대금")
                date = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "일자")
                start_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "시가")
                high_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "고가")
                low_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "저가")

                data.append("")
                data.append(current_price.strip())
                data.append(value.strip())
                data.append(trading_value.strip())
                data.append(date.strip())
                data.append(start_price.strip())
                data.append(high_price.strip())
                data.append(low_price.strip())
                data.append("")

                self.calcul_data.append(data.copy())

            if sPrevNext == "2":
                self.day_kiwoom_db(code=code, sPrevNext=sPrevNext)
    
            ''' '''
            else:
                print("총일수 %s" % len(self.calcul_data))
                pass_success = False
                # 120일 이평선을 그릴만큼의 데이터가 있는가?
                if self.calcul_data == None or len(self.calcul_data) < 120:
                    pass_success = False
                else:
                    # 기울기 구하는 변수들
                    a = int(self.calcul_data[0][1]) #1일
                    b = int(self.calcul_data[16][1]) #16일
                    total_price1, total_price2 , smallest1, smallest2, largest1, largest2 = 0,0,b,a,b,a
                    count, count_above1 ,count_below1, count_above2, count_below2 = 0,0,0,0,0


                    for value in self.calcul_data[16:31]:  # 16부터 30일 전까지
                        total_price1 += int(value[1])  # 15읠 종가를 다 더한것
                        count += 1
                        if int(value[1]) <= smallest1 :
                            smallest1 = int(value[1])
                            count_below1 = count

                        if int(value[1]) >= largest1 :
                            largest1 = int(value[1])
                            count_above1 = count

                    #기울기를 구하는 포인트점, 최고가 최저가 구하는 for문
                    for value in self.calcul_data[:15]:  # 오늘부터 15일 전까지
                        total_price2 += int(value[1])  # 15 종가를 다 더한것
                        count += 1
                        if int(value[1]) <= smallest2 :
                            smallest2 = int(value[1])
                            count_below2 = count

                        if int(value[1]) > largest2:
                            largest2 = int(value[1])
                            count_above2 = count

                  
                    inclination_above = (largest2 - largest1) / (count_above2 - count_above1)
                    inclination_below = (smallest2-smallest1) / (count_below2 - count_below1)
                    print(largest2,"-",largest1,"=",(largest2 - largest1))

                    print("-----------------------------------------------------------------")
                    print(count_above2,"-",count_above1,"=",(count_above2 - count_above1))
                    print("  ")
                    print("  ")
                    print("  ")
                    print(smallest2,"-",smallest1,"=",(smallest2-smallest1))
                    print("-----------------------------------------------------------------")
                    print(count_below2,"-", count_below1,"=",(count_below2 - count_below1))

                    print(inclination_above)
                    print(inclination_below)

                    #종목별 기울기 저장
                    self.stock_count +=1
                    if self.stock_count == 1:
                        self.inclination_above1 = inclination_above
                        self.inclination_below1 = inclination_below
                        self.intercept_above1 = largest1
                        self.intercept_below1 = smallest1
                        print(self.inclination_above1,"+",self.intercept_above1)
                        print(self.inclination_below1,"+",self.intercept_below1)


                    elif self.stock_count == 2:
                        self.inclination_above2 = inclination_above
                        self.inclination_below2 = inclination_below
                        self.intercept_above2 = largest1
                        self.intercept_below2 = smallest1
                        print(self.inclination_above2,"+",self.intercept_above2)
                        print(self.inclination_below2,"+",self.intercept_below2)

                
                
                self.calcul_data.clear()
                self.calculator_event_loop.exit()

        elif sRQName == "주식분봉차트조회":
            code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "종목코드")
            code = code.strip()  # 불러온 데이터는 strip를 통해 여백을 없앤다.
            print("%s 분봉데이터 요청" % code)

            cnt = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)  # GetRepeatCnt API멀티데이터 불러옴
            print("데이터 분봉수 %s" % cnt)

            # 한번 조회하면 600일치까지 일봉데이터를 받을 수 있다.
            # data = self.dynamicCall("getCommDataEx(QSting, QString)", strCode, sRQName)
            # 아래는 데이터의 형태
            # [["", "현재가", "거래량", "체결시간","시가", "고가", "저가", ""], ["", "현재가", "거래량", "체결시간","시가", "고가", "저가", ""]]
            #  0      1        2        3       4      5      6
            for i in range(cnt):
                data = []
                current_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"현재가")
                value = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "거래량")
                trading_time = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"체결시간")
                start_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "시가")
                high_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "고가")
                low_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "저가")

                data.append("")
                data.append(current_price.strip())
                data.append(value.strip())
                data.append(trading_time.strip())
                data.append(start_price.strip())
                data.append(high_price.strip())
                data.append(low_price.strip())
                data.append("")

                self.calcul_data_m.append(data.copy())
                print(self.calcul_data_m)

            if sPrevNext == "2":
                self.day_kiwoom_db2(code=code, sPrevNext=sPrevNext)
           # else :


            self.calculator_event_loop2.exit()

    # ---END---- def trdata_slot-------------------------------##

    # 1 매매조건, 대과거는 평균선위에, 중간과거는 평균선 밑에 현재는 일봉이 평균선과 만났을 때 매매, 120일 편균선
    # preNext 600개 데이터를 초과시 담음 페이지로 넘겨줄떄사용
    ###market_code개발가이드 기타함수
    # 0: 장내,10: 코스닥, 3: ELW, 8: ETF, 50: KONEX, 4: 뮤추얼펀드, 5: 신주인수권 , 6: 리츠, 9: 하이얼펀드 ,30: K - OTC

    def get_code_list_by_market(self, market_code):  # market_code 10(코스닥)넘겨줌  #종목코드를 불러옴
        '''
        종목코드를 반환
        :param market_code:
        :return:
        '''
        code_list = self.dynamicCall("GetCodeListByMarket(QString)", market_code)
        code_list = code_list.split(";")[:-1]  # 마지막은 공백이니 -1마지막 리스트를 넣지 않는다.
        return code_list

    def calculator_fnc(self): #일 단위
        '''
        종목분석 실행용 함수
        :return:
        '''
        code_list = self.get_code_list_by_market("10")
        print("코스닥 갯수 %s" % len(code_list))

        for idx, code in enumerate(code_list):
            self.dynamicCall("DisconnectRealData(QString)", self.screen_calculation_stock)
            print("%s / %s : KOSDAQ Stock Code : %s is updating" % (idx + 1, len(code_list), code))
            self.day_kiwoom_db(code=code)

    def calculator_fnc2(self): # 새로운 방식
        '''
        종목분석 실행용 함수
        :return:
        '''
        #code_list = self.get_code_list_by_market("10")
        print(" 종목 갯수 %s" % len(self.account_stock_dict))

        for idx, code in enumerate(self.account_stock_dict):
            self.dynamicCall("DisconnectRealData(QString)", self.screen_calculation_stock)
            print("%s / %s : KOSDAQ Stock Code : %s is updating" % (idx + 1, len(self.account_stock_dict), code))
            self.day_kiwoom_db(code=code)

    def day_kiwoom_db(self, code=None, date=None, sPrevNext="0"):  # #TR요청 데이터를 불러옴, 시그널요청
        # 키움api는 3.6초 보다 빨리 요청하면 에러가 생김
        QTest.qWait(3600)  # 3.6초 딜레이 시켜서 요청함 # time.sleep(o.2)

        self.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        self.dynamicCall("SetInputValue(QString, QString)", "수정주가부분", "1")

        if date != None:
            self.dynamicCall("SetInputValue(QString, QString)", "기준일자", date)

        self.dynamicCall("CommRqData(String, String, int, String)", "주식일봉차트조회", "opt10081", sPrevNext,
                         self.screen_calculation_stock)  # TR서버로 전송- transaction
        self.calculator_event_loop.exec_()

    def day_kiwoom_db2(self, code=None, date=None, sPrevNext="0"):  #분봉용
        # 키움api는 3.6초 보다 빨리 요청하면 에러가 생김
        QTest.qWait(3600)  # 3.6초 딜레이 시켜서 요청함 # time.sleep(o.2)

        self.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        self.dynamicCall("SetInputValue(QString, QString)", "수정주가부분", "1")

        self.dynamicCall("SetInputValue(QString, QString)", "틱범위", "3")

        self.dynamicCall("CommRqData(String, String, int, String)", "주식분봉차트조회", "opt10080", sPrevNext,
                         self.screen_calculation_stock)  # TR서버로 전송- transaction
        self.calculator_event_loop2.exec_()



    # 선별된 종목을 딕셔너리에 저장
    def read_code(self):
        if os.path.exists("files/condition_stocks.txt"):
            f = open("files/condition_stocks.txt", "r", encoding="utf8")

            lines = f.readlines()
            for line in lines:  # 한줄씩
                if line != "":  # 라인이 비어있지 않을 경우
                    ls = line.split("\t")  # ["202342(종목번호)", "종목명","현재가"\n]
                    stock_code = ls[0]
                    stock_name = ls[1]
                    stock_price = int(ls[2].split("\n")[0])  # ["2023(현재가)",""] 이중 앞에 것을 가져오기위해 0
                    stock_price = abs(stock_price)  # 현재가가 하락일경우 -로 표시됨, 그러므로 절대값 씌운다.

                    # 주식종목을 볼때는 아래 딕셔너리만 사용을 할 것이다.
                    self.portfolio_stock_dict.update({stock_code: {"종목명": stock_name, "현재가": stock_price}})
            f.close()
            print(self.portfolio_stock_dict)

    def screen_number_setting(self):
        screen_overwrite = []

        # 계좌평가잔고내역에 있는 종목들 불러옴
        for code in self.account_stock_dict.keys():
            if code not in screen_overwrite:
                screen_overwrite.append(code)

        # 미체결에 있는 종목들
        for order_number in self.outstanding_share_dict.keys():
            code = self.outstanding_share_dict[order_number]['종목코드']

            if code not in screen_overwrite:
                screen_overwrite.append(code)

        # 포트폴리오에 담겨있는 종목들 = 엄선된 종목
        for code in self.portfolio_stock_dict.keys():
            if code not in screen_overwrite:
                screen_overwrite.append(code)

        # 사용할 종목들 딕셔너리 정리 + 스크린 번호 딕셔너리에 추가하는 부분
        cnt = 0
        for code in screen_overwrite:
            temp_screen = int(self.screen_real_stock)
            meme_screen = int(self.screen_meme_stock)

            # 스크린번호 하나당 종목코드 50개씩 할당 //원래는 100개까지 가능
            if (cnt % 50) == 0:
                temp_screen += 1  # 5000 -> 5001
                self.screen_real_stock = str(temp_screen)
            if (cnt % 50) == 0:
                meme_screen += 1
                self.screen_meme_stock = str(meme_screen)

            # 앞서 저장한 사용할 모든 종목 screen_overwrite를 portfolio_stock_dict에 저장
            if code in self.portfolio_stock_dict.keys():  # 종목코드 있을시
                self.portfolio_stock_dict[code].update({"스크린번호": str(self.screen_real_stock)})
                self.portfolio_stock_dict[code].update({"주문용스크린번호": str(self.screen_meme_stock)})

            elif code not in self.portfolio_stock_dict.keys():  # 계좌평가잔고내역과 미체결종목들을 딕셔너리에 추가
                self.portfolio_stock_dict.update(
                    {code: {"스크린번호": str(self.screen_real_stock), "주문용스크린번호": str(self.screen_meme_stock)}})

            cnt += 1
        print(self.portfolio_stock_dict)

    # w
    def realdata_slot(self, sCode, sRealType, sRealData):
        if sRealType == "장시작시간":
            fid = self.readType.REALTYPE[sRealType]['장운영구분']
            value = self.dynamicCall("GetCommRealData(QString, int)", sCode, fid)
            print("a")

            if value == "0":
                print("장 시작 전")
            elif value == '3':
                print("장 시작")
            elif value == "2":
                print("장 종료, 동시호가로 넘어감")
            elif value == "4":
                print("3시30분 장 종료")
                for code in self.portfolio_stock_dict.keys():
                    self.dynamicCall("SetRealRemove(String, String)", self.portfolio_stock_dict[code]['스크린번호'], code)

                # 장끝나면  파일삭제하고 다시 함수를 돌리고 나간다.
                # QTest.qWait(5000)

                # self.file_delete()
                # self.calculator_fnc()
                sys.exit()
        elif sRealType == "주식체결":
            a = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.readType.REALTYPE[sRealType]['체결시간'])
            b = self.dynamicCall("GetCommRealData(QString, int)", sCode,
                                 self.readType.REALTYPE[sRealType]['현재가'])  # +(_) 2500
            b = abs(int(b))

            c = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.readType.REALTYPE[sRealType]['전일대비'])
            c = abs(int(c))

            d = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.readType.REALTYPE[sRealType]['등락율'])
            d = float(d)

            e = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.readType.REALTYPE[sRealType]['(최우선)매도호가'])
            e = abs(int(e))

            f = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.readType.REALTYPE[sRealType]['(최우선)매수호가'])
            f = abs(int(f))

            g = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.readType.REALTYPE[sRealType]['거래량'])
            g = abs(int(g))

            h = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.readType.REALTYPE[sRealType]['누적거래량'])
            h = abs(int(h))

            i = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.readType.REALTYPE[sRealType]['고가'])
            i = abs(int(i))

            j = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.readType.REALTYPE[sRealType]['시가'])
            j = abs(int(j))

            k = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.readType.REALTYPE[sRealType]['저가'])
            k = abs(int(k))

            if sCode not in self.portfolio_stock_dict:
                self.portfolio_stock_dict.update({sCode: {}})

            self.portfolio_stock_dict[sCode].update({"체결시간": a})
            self.portfolio_stock_dict[sCode].update({"현재가": b})
            self.portfolio_stock_dict[sCode].update({"전일대비": c})
            self.portfolio_stock_dict[sCode].update({"등락율": d})
            self.portfolio_stock_dict[sCode].update({"(최우선)매도호가": e})
            self.portfolio_stock_dict[sCode].update({"(최우선)매수호가": f})
            self.portfolio_stock_dict[sCode].update({"거래량": g})
            self.portfolio_stock_dict[sCode].update({"누적거래량": h})
            self.portfolio_stock_dict[sCode].update({"고가": i})
            self.portfolio_stock_dict[sCode].update({"시가": j})
            self.portfolio_stock_dict[sCode].update({"저가": k})

            print(self.portfolio_stock_dict[sCode])
            print("c")

            # 실시간 데이터가 오면 매수할지 매도할지 결정
            # 계좌잔고평가내역에 있고 오늘 산 잔고에는 없을 경우  #jango_dict = 오늘 산 종목
            if sCode in self.account_stock_dict.keys() and sCode not in self.jango_dict.key():
                print("%s %s" % ("신규매도를 한다", sCode))
                asd = self.account_stock_dict[sCode]

                meme_rate = (b - asd["매입가"]) / asd["매입가"] * 100  # 등락율 구하기

                if asd["매매가능수량"] > 0 and (meme_rate > 5 or meme_rate < -5):
                    oredr_success = self.dynamicCall(
                        "SendOrder(QString,QString,QString,int,QString,int,int,QString,QString)",
                        ["신규매도", self.portfolio_stock_dict[sCode]["주문용스크린번호"], self.account_num, 2,
                         sCode, asd["매매가능수량"], 0, self.readType.SENDTYPE['거래구분']['시장가'], ""])  # 빈칸이 원주문 번호
                    if oredr_success == 0:
                        print("매도주문 전달 성공")
                        del self.account_stock_dict[sCode]
                    else:
                        print("매도주문 전달 실패")

                # 오늘 산 잔고에 있을 경우
            elif sCode in self.jango_dict.keys():
                jd = self.jango_dict.keys()
                meme_rate = (b - jd['매입단가']) / jd('매입단가') * 100

                if jd["주문가능수량"] > 0 and (meme_rate > 5 or meme_rate < -5):
                    oredr_success = self.dynamicCall(
                        "SendOrder(QString,QString,QString,int,QString,int,int,QString,QString)",
                        ["신규매도", self.portfolio_stock_dict[sCode]["주문용스크린번호"], self.account_num, 2,
                         sCode, jd["주문가능수량"], 0, self.readType.SENDTYPE['거래구분']['시장가'], ""])  # 빈칸이 원주문 번호
                    if oredr_success == 0:
                        print("매도주문 전달 성공")
                    else:
                        print("매도주문 전달 실패")

                # 등락율이 2.0% 이상이고 오늘 산 잔고에 없을 경우
            elif d > 2.0 and sCode not in self.jango_dict:
                print("%s %s", ("신규매수를 한다.", sCode))
                result = (self.use_money * 0.1) / e  # e는 현재가
                quantity = int(result)

                order_success = self.dynamicCall(
                    "SendOrder(QString,QString,QString,int,QString,int,int,QString,QSTring)",
                    ["신규매수", self.portfolio_stock_dict[sCode]["주문용스크린번호"], self.account_num, 1, sCode, quantity, e,
                     self.readType.SENDTYPE['거래구분']['지정가'], ""])
                # 지정가는 자신이 지정한 지정가
                if order_success == 0:
                    print("매수주문 전달 성공")
                else:
                    print("매수주문 전달 실패")

            not_meme_list = list(self.outstanding_share_dict)  # 새로운 주소에 배당 + .copy() 가능
            for order_num in not_meme_list:
                code = self.outstanding_share_dict[order_num]["종목코드"]
                meme_price = self.outstanding_share_dict[order_num]["주문가격"]
                not_quantity = self.outstanding_share_dict[order_num]["미체결수량"]
                order_gubun = self.outstanding_share_dict[order_num]["주문구분"]

                if order_gubun == "신규매수" and not_quantity > 0 and e > meme_price:
                    order_success = self.dynamicCall(
                        "SendOrder(QString,QString,QString,int,QString,int,int,QString,QSTring)",
                        ["매수취소", self.portfolio_stock_dict[sCode]["주문용스크린번호"], self.account_num, 3, code, 0, 0,
                         self.readType.SENDTYPE['거래구분']['지정가'], order_num]
                    )  # 3 = 매수취소를 뜻함, 0= 전량취소 ordernum을 쓰는 이유는 어떤 것을 취소할지 알기 위함
                    if order_success == 0:
                        print("매수취소 전달 성공")
                    else:
                        print("매수취소 전달 실패")


                elif not_quantity == 0:  # 미채결수량이 0이면
                    del self.outstanding_share_dict[order_num]

    def chejan_slot(self, sGubun, nItemCnt, sFIdList):

        if int(sGubun) == "0":
            account_num = self.dynamicCall("GetChejanData(int)", self.readType.REALTYPE['주문체결']['계좌번호'])
            sCode = self.dynamicCall("GetChejanData(int)", self.readType.REALTYPE['주문체결']['종목코드'])[1:]
            stock_name = self.dynamicCall("GetChejanData(int)", self.readType.REALTYPE['주문체결']['종목명'])
            stock_name = stock_name.strip()

            origin_order_number = self.dynamicCall("GetChejanData(int)",
                                                   self.readType.REALTYPE['주문체결']['원주문번호'])  # defaluse : "000000"
            order_number = self.dynamicCall("GetChejanData(int)",
                                            self.readType.REALTYPE['주문체결']['주문번호'])  # 출력 : 0115061 마지막 주문번호

            order_status = self.dynamicCall("GetChejanData(int)",
                                            self.readType.REALTYPE['주문체결']['주문상태'])  # 출력 : 점수, 확인, 체결

            order_quan = self.dynamicCall("GetChejanData(int)", self.readType.REALTYPE['주문체결']['주문수량'])  # 출력 : 3
            order_quan = int(order_quan)

            order_price = self.dynamicCall("GetChejanData(int)", self.readType.REALTYPE['주문체결']['주문가격'])  # 출력 : 가격
            order_price = int(order_price)

            not_chegual_quan = self.dynamicCall("GetChejanData(int)",
                                                self.readType.REALTYPE['주문체결']['미체결수량'])  # 출력 : 15, default : 0
            not_chegual_quan = int(not_chegual_quan)

            order_gubun = self.dynamicCall("GetChejanData(int)",
                                           self.readType.REALTYPE['주문체결']['주문구분'])  # 출력 : -매도, +매수
            order_gubun = order_gubun.strip().lstrip('+').lstrip('-')

            chegual_time_str = self.dynamicCall("GetChejanData(int)", self.readType.REALTYPE['주문체결']['주문/체결시간'])

            chegual_price = self.dynamicCall("GetChejanData(int)", self.readType.REALTYPE['주문체결']['체결가'])

            if chegual_price == '':
                chegual_price = 0
            else:
                chegual_price = int(chegual_price)

            chegual_quantity = self.dynamicCall("GetChejanData(int)",
                                                self.readType.REALTYPE['주문체결']['체결량'])  # default = ''

            if chegual_quantity == '':
                chegual_quantity = 0
            else:
                chegual_quantity = int(chegual_quantity)

            current_price = self.dynamicCall("GetChejanData(int)", self.readType.REALTYPE['주문체결']['현재가'])
            current_price = abs(int(current_price))

            first_sell_price = self.dynamicCall("GetChejanData(int)", self.readType.REALTYPE['주문체결']['(최우선)매도호가'])
            first_sell_price = abs(int(first_sell_price))

            first_buy_price = self.dynamicCall("GetChejanData(int)", self.readType.REALTYPE['주문체결']['(최우선)매수호가'])
            first_buy_price = abs(int(first_buy_price))

            # 딕셔너리 업데이트 // 새로 들어온 주문이면 주문번호 할당
            if order_number not in self.outstanding_share_dict.keys():
                self.outstanding_share_dict.update({order_number: {}})

            self.outstanding_share_dict[order_number].update({"종목코드": sCode})
            self.outstanding_share_dict[order_number].update({"주문번호": order_number})
            self.outstanding_share_dict[order_number].update({"종목명": stock_name})
            self.outstanding_share_dict[order_number].update({"주문상태": order_status})
            self.outstanding_share_dict[order_number].update({"주문수량": order_quan})
            self.outstanding_share_dict[order_number].update({"주문가격": order_price})
            self.outstanding_share_dict[order_number].update({"미체결수량": not_chegual_quan})
            self.outstanding_share_dict[order_number].update({"원주문번호": origin_order_number})
            self.outstanding_share_dict[order_number].update({"주문구분": order_gubun})
            self.outstanding_share_dict[order_number].update({"주문/체결시간": chegual_time_str})
            self.outstanding_share_dict[order_number].update({"체결가": chegual_price})
            self.outstanding_share_dict[order_number].update({"체결량": chegual_quantity})
            self.outstanding_share_dict[order_number].update({"현재가": current_price})
            self.outstanding_share_dict[order_number].update({"(최우선)매도호가": first_sell_price})
            self.outstanding_share_dict[order_number].update({"(최우선)매수호가": first_buy_price})


        elif int(sGubun) == "1":
            account_num = self.dynamicCall("GetChejanData(int)", self.readType.REALTYPE['잔고']['계좌번호'])
            sCode = self.dynamicCall("GetChejanData(int)", self.readType.REALTYPE['잔고']['종목코드'])[1:]

            stock_name = self.dynamicCall("GetChejanData(int)", self.readType.REALTYPE['잔고']['종목명'])
            stock_name = stock_name.strip()

            current_price = self.dynamicCall("GetChejanData(int)", self.readType.REALTYPE['잔고']['현재가'])
            current_price = abs(int(current_price))

            stock_quan = self.dynamicCall("GetChejanData(int)", self.readType.REALTYPE['잔고']['보유수량'])
            stock_quan = int(stock_quan)

            like_quan = self.dynamicCall("GetChejanData(int)", self.readType.REALTYPE['잔고']['주문가능수량'])
            like_quan = int(like_quan)

            buy_price = self.dynamicCall("GetChejanData(int)", self.readType.REALTYPE['잔고']['매입단가'])
            buy_price = abs(int(buy_price))

            total_buy_price = self.dynamicCall("GetChejanData(int)", self.readType.REALTYPE['잔고']['총매입가'])
            total_buy_price = int(total_buy_price)

            meme_gubun = self.dynamicCall("GetChejanData(int)", self.readType.REALTYPE['잔고']['매도매수구분'])
            meme_gubun = self.readType.REALTYPE['매도수구분'][meme_gubun]

            first_sell_price = self.dynamicCall("GetChejanData(int)", self.readType.REALTYPE['잔고']['(최우선)매도호가'])
            first_sell_price = abs(int(first_sell_price))

            first_buy_price = self.dynamicCall("GetChejanData(int)", self.readType.REALTYPE['잔고']['(최우선)매수호가'])
            first_buy_price = abs(int(first_buy_price))

            if sCode not in self.jango_dict.keys():
                self.jango_dict.update({sCode: {}})

            self.jango_dict[sCode].update({"현재가": current_price})
            self.jango_dict[sCode].update({"종목코드": sCode})
            self.jango_dict[sCode].update({"종목명": stock_name})
            self.jango_dict[sCode].update({"보유수량": stock_quan})
            self.jango_dict[sCode].update({"주문가능수량": like_quan})
            self.jango_dict[sCode].update({"매입단가": buy_price})
            self.jango_dict[sCode].update({"총매입가": total_buy_price})
            self.jango_dict[sCode].update({"메도매수구분": meme_gubun})
            self.jango_dict[sCode].update({"(최우선)매도호가": first_sell_price})
            self.jango_dict[sCode].update({"(최우선)매수호가": first_buy_price})

            if stock_quan == 0:
                del self.jango_dict[sCode]  # 끝까지 확인하고 매매한거 딕셔너리에서 삭제
                self.dynamicCall("SetRealRemove(QString, QString)", self.portfolio_stock_dict[sCode]['스크린번호'], sCode)

    # 송수신 메세지 get
    def msg_slot(self, sScrNo, sRQName, sTrCode, msg):
        print("스크린:%s, 요청이름:%s, tr코드 : %s --- %s" % (sScrNo, sRQName, sTrCode, msg))

    # 파일삭제
    def file_delete(self):
        if os.path.isfile("files/condition_stock.txt"):
            os.remove("files/condition_stock.txt")

    # 66
