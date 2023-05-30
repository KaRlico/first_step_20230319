from selenium import webdriver
from bs4 import BeautifulSoup
from konlpy.tag import Twitter
import urllib.request
import re
import sys
import time
import os
from os.path import exists
import matplotlib.pyplot as plt
import nltk
from matplotlib import font_manager, rc
from pylab import rcParams
from matplotlib import pylab
import pandas as pd
from selenium.webdriver.common.keys import Keys
import matplotlib.image as mpimg
import IPython
IPython.get_ipython().run_line_magic('matplotlib', 'notebook')
t = Twitter()
def create_url():
    print('마켓컬리 리뷰 크롤링 프로그램을 시작합니다.','\n')
    phantom_path = input(r'phantomjs 파일 위치를 지정해주세요(ex.C:\Users\phantomjs-2.1.1-windows\bin\phantomjs.exe) : ')
    phantom_path2 = phantom_path.replace('\\','/')
    try:
        driver = webdriver.PhantomJS(executable_path=phantom_path2) #팬텀JS 위치지정하기)
    except:
        sys.exit('phamtomjs 파일 위치가 잘못되었습니다. 프로그램을 종료합니다.')
    print('URL값을 가져오는 중입니다. 잠시만 기다려주세요...','\n')
    driver.implicitly_wait(3)    
    driver.get('http://www.kurly.com/shop/goods/goods_review.php') #url로 들어가기
    
    html = driver.page_source
    soup = BeautifulSoup(html, "lxml")

    notices = soup.select('div.layout-wrapper.goods-view-area > div.xans-board-title > form > table.xans-board-search.all_review_sort > tbody > tr > td.input_txt > select.select')
    div1 = list(notices[0]) # notices[0]이 1차분류값이므로 해당 값을 리스트화시켜서 한개씩 패치하도록함 
    div1_dic = {} #1차분류에 대해 분류값과 number 값 묶기 
    
    #1차분류의 키와 값 만들기 
    for div1_index in range(len(div1)):
        number = re.findall('\d+',str(div1[div1_index]))[0]
        if number.find('0') == -1:
            continue
        else:
            div1_dic[div1[div1_index].get_text()] = number  
    return driver, div1_dic


def select_url():
    #검색할 값 지정 
    put = 0
    driver, div1_dic = create_url()
    for i in div1_dic.keys():
        print(i)
    while put not in div1_dic:
        put = input('크롤링 할 대상을 목록에서 선택해주세요(전체일경우 전체 라고 입력해주세요) : ')
        if put == '전체':
            break
        if put not in div1_dic:
            print('대상이 목록에 없습니다. 띄어쓰기 혹은 맞춤법을 확인해주세요','\n')
    return driver,put,div1_dic







def croll_url():
    #크롤링 시작
    product_dic = {}
    product_analysis = {}
    driver, put, div1_dic = select_url()
    print(put+'에 대해서 크롤링을 시작합니다.','\n')
    if put == '전체':
        list_url = 'http://www.kurly.com/shop/goods/goods_review.php'
    else:
        list_url = 'http://www.kurly.com/shop/goods/goods_review.php?skey=all&cate[0]='+div1_dic[put]+'&sort=1&page_num=20&page=1'
    url = urllib.request.Request(list_url)
    res = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(res,'lxml')
    page = soup.select_one('a.layout-pagination-button.layout-pagination-last-page')
    if page == None:
        sys.exit('리뷰가 없습니다. 프로그램을 종료합니다')
    else:
        page_cnt = page.get('href')[page.get('href').find('page=')+5:]
    
    print(put+'의 리뷰 페이지는 총 '+page_cnt+' 페이지 입니다.','\n')
    select_page = 0
    while select_page == 0 or select_page not in range(1,int(page_cnt)+1):
        select_page = int(input('검색할 페이지 수를 설정하세요(1 ~'+page_cnt+') : '))
        if select_page == 0 or select_page > int(page_cnt):
            print('검색할 페이지가 최대페이지보다 크거나 0입니다.','\n')
    cnt = 0        
    for page in range(1,select_page+1):
        if put == '전체':
            list_url2 = 'http://www.kurly.com/shop/goods/goods_review.php?&page='+str(page)
        else:
            list_url2 = 'http://www.kurly.com/shop/goods/goods_review.php?skey=all&cate[0]='+div1_dic[put]+'&sort=1&page_num=20&page='+str(page)
        url2 = urllib.request.Request(list_url2)
        time.sleep(2)
        res2 = urllib.request.urlopen(url2).read()
        time.sleep(2)
        soup2 = BeautifulSoup(res2,'lxml')
        time.sleep(2)
        product = soup2.findAll('td',{'class':'thumb'}) # 리뷰 상품명
        review1 = soup2.findAll('td',{'class':'txt_title'}) # 리뷰 제목
        review2 = soup2.findAll('div',{'width':'100%'}) # 리뷰 본문
        review_like = soup2.findAll('span',{'class':'review-like-cnt'}) # 리뷰 좋아요
        review_hit = soup2.findAll('span',{'class':'review-hit-cnt'}) # 리뷰 조회수 
        cnt += 1
    
        for pro,rev1,rev2,revlike,revhit in zip(product,review1,review2,review_like,review_hit): # put 제품에 대해 크롤링해서 product_dic에 dict형식으로 집어넣음 value index 0번이 리뷰제목+리뷰본문, 1번이 좋아요, 2번이 조회수 
            if pro.get_text(strip=True) not in product_dic:
                if pro.get_text(strip=True) == '':
                    continue
                else:
                    if rev1.get_text(strip=True) == 'Love food, Love life!' or '고객님' in rev1.get_text(strip=True) :
                        continue
                    else:
                        product_dic[pro.get_text(strip=True)] = (rev1.get_text(strip=True), rev2.get_text(strip=True)), int(revlike.get_text(strip=True)), int(revhit.get_text(strip=True))
            else:
                if rev1.get_text(strip=True) == 'Love food, Love life!' or '고객님' in rev1.get_text(strip=True) :
                    continue
                else:
                    product_dic[pro.get_text(strip=True)] = product_dic[pro.get_text(strip=True)][0] + (rev1.get_text(strip=True), rev2.get_text(strip=True)), product_dic[pro.get_text(strip=True)][-2] + int(revlike.get_text(strip=True)), product_dic[pro.get_text(strip=True)][-1] + int(revhit.get_text(strip=True))
        print(str(page)+' page 완료')
        
    for rev_cnt_keys in product_dic.keys():
        product_dic[rev_cnt_keys] = product_dic[rev_cnt_keys][0],product_dic[rev_cnt_keys][1],product_dic[rev_cnt_keys][2],int(len(product_dic[rev_cnt_keys][0])/2)

    for pro_name in product_dic.keys():
        for pro_review in product_dic[pro_name][0]:
            a = t.pos(pro_review, norm=True, stem=True)
            for i in a:
                if i[1] == 'Josa' or i[1] == 'Punctuation' or i[1] == 'Foreign':
                    continue
                else:
                    if pro_name not in product_analysis:
                        product_analysis[pro_name] = i[0],0,0,0
                    else:
                        product_analysis[pro_name] = product_analysis[pro_name][0]+' '+i[0],0,0,0
        pro_revlike, pro_revhit, pro_revcnt = product_dic[pro_name][1:]
        product_analysis[pro_name] = product_analysis[pro_name][0],pro_revlike,pro_revhit,pro_revcnt
        
    
    print(str(cnt)+'페이지에 대해 크롤링을 완료하였습니다.','\n')
    
    return driver, product_dic, product_analysis


def croll_cretext():
    driver, product_dic, product_analysis = croll_url()
    put = None
    save = None
    
    while save != 'Y':
        save = input('결과를 txt 파일로 저장할까요?(Y/N) : ').upper()
        if save == 'N':
            return driver, product_dic,product_analysis
        elif save != 'Y':
            print('Y 또는 N 으로 입력해주세요')
                    
    print('\n\n'+'한국어에 대한 단어추출은 정확하지 않을 수 있습니다.')   
             
    while put != '원본':
        put = input('어떤 결과로 저장할까요 (원본/단어만추출/둘다) : ').upper()
        if put == '단어만추출':
            break
        if put == '둘다':
            put2 = '둘다'
            break
        elif put != '원본':
            print('원본 또는 단어만추출 또는 둘다 로 입력해주세요')
        
    if put == '원본' or put2 == '둘다':
        print('\n\n'+'원본을 저장합니다.')
        print('원본 결과는 txt 파일로 저장됩니다.')
        file = input('파일명을 입력해주세요(C:\kurlycroll 에 저장됩니다) : ')
        if not exists('C:/kurlycroll'):
            os.mkdir('C:/kurlycroll')
            print('C:\kurlycroll 폴더를 생성했습니다.')
        else:
            print('C:\kurlycroll 폴더가 이미 존재합니다.')
        if exists('C:/kurlycroll/'+file+'.txt'):
            same_file = None
            while same_file != 'Y':
                same_file = input('동일한 파일이 존재합니다. 덮어씌울까요?(Y/N) : ').upper()
                if same_file == 'N':
                    break
                elif same_file != 'Y':
                    print('Y 또는 N 으로 입력해주세요')
            if same_file == 'Y':
                print('파일을 덮어씌웁니다.')
                with open('C:/kurlycroll/'+file+'.txt', 'w', -1, 'utf-8') as f :
                    for i,j in product_dic.items():
                        f.write('product_name = '+i+'\n') # 제품명
                        cnt = 0
                        for k in j[0]: 
                            cnt += 1
                            if cnt % 2 == 0:
                                f.write(k+'\n\n')
                            else:
                                f.write('리뷰제목 : '+k+'\n')
    
                        for v in range(len(j[1:])):    
                            if v % 3 == 0:
                                data = '좋아요 '+str(j[1:][v])+' '
                                f.write(data)
                            elif v % 3 == 1:
                                data = '조회수 '+str(j[1:][v])+' '
                                f.write(data)
                            else:
                                data = '리뷰갯수' + str(j[1:][v])
                                f.write(data)
                print('파일을 생성하였습니다.')
            else:
                if put == '둘다':
                    print('파일을 덮어씌우지 않았습니다.')
                else:
                    return driver, product_dic,product_analysis
        else:
            print('text를 생성합니다.')
            with open('C:/kurlycroll/'+file+'.txt', 'w', -1, 'utf-8') as f2 :
                for i,j in product_dic.items():
                    f2.write('product_name = '+i+'\n') # 제품명
                    cnt = 0
                    for k in j[0]: 
                        cnt += 1
                        if cnt % 2 == 0:
                            f2.write(k+'\n\n')
                        else:
                            f2.write('리뷰제목 : '+k+'\n')

                    for v in range(len(j[1:])):    
                        if v % 3 == 0:
                            data = '좋아요 '+str(j[1:][v])+' '
                            f2.write(data)
                        elif v % 3 == 1:
                            data = '조회수 '+str(j[1:][v])+' '
                            f2.write(data)
                        else:
                            data = '리뷰갯수' + str(j[1:][v])
                            f2.write(data) 
            print('파일을 생성하였습니다.')


    if put == '단어추출' or put2 == '둘다':
        print('\n\n'+'단어추출을 저장합니다.')
        print('단어추출 결과는 txt 파일로 저장됩니다.')
        file2 = input('파일명을 입력해주세요(C:\kurlycroll 에 저장됩니다) : ')
        if not exists('C:/kurlycroll'):
            os.mkdir('C:/kurlycroll')
            print('C:\kurlycroll 폴더를 생성했습니다.')
        else:
            print('C:\kurlycroll 폴더가 이미 존재합니다.')
        if exists('C:/kurlycroll/'+file2+'.txt'):
            same_file2 = None        
            while same_file2 != 'Y':
                same_file2 = input('동일한 파일이 존재합니다. 덮어씌울까요?(Y/N) : ').upper()
                if same_file2 == 'N':
                    break
                elif put != 'Y':
                    print('Y 또는 N 으로 입력해주세요')
            if same_file2 == 'Y':
                print('파일을 덮어씌웁니다.')
                with open('C:/kurlycroll/'+file2+'.txt', 'w', -1, 'utf-8') as f3 :
                    for q,w in product_analysis.items():
                        f3.write('product_name = '+q+'\n') # 제품명
                        f3.write('단어추출결과 : '+w[0]+'\n')
                        for e in range(len(w[1:])):    
                            if e % 3 == 0:
                                data = '좋아요 '+str(w[1:][e])+' '
                                f3.write(data)
                            elif e % 3 == 1:
                                data = '조회수 '+str(w[1:][e])+' '
                                f3.write(data)
                            else:
                                data = '리뷰갯수' + str(w[1:][e])
                                f3.write(data)
                print('파일을 생성하였습니다.')
            else:
                return driver, product_dic,product_analysis

        else:
            print('text를 생성합니다.')
            with open('C:/kurlycroll/'+file2+'.txt', 'w', -1, 'utf-8') as f4 :
                for q,w in product_analysis.items():
                    f4.write('product_name = '+q+'\n') # 제품명
                    f4.write('단어추출결과 : '+w[0]+'\n')
                    for e in range(len(w[1:])):    
                        if v % 3 == 0:
                            data = '좋아요 '+str(w[1:][e])+' '
                            f4.write(data)
                        elif v % 3 == 1:
                            data = '조회수 '+str(w[1:][e])+' '
                            f4.write(data)
                        else:
                            data = '리뷰갯수' + str(w[1:][e])
                            f4.write(data)
            print('파일을 생성하였습니다.')
    
    return driver, product_dic,product_analysis

def croll_graph():
    driver, product_dic,product_analysis = croll_cretext()
    
    print('그래프는 단어추출된 결과로만 표시됩니다.')
    save_graph = None
    while save_graph != 'Y':
            save_graph = input('결과를 그래프로 저장할까요?(Y/N) : ').upper()
            if save_graph == 'N':
                return driver, product_dic
            elif save_graph != 'Y':
                print('Y 또는 N 으로 입력해주세요')
    
    font_name = font_manager.FontProperties(fname="c:/Windows/Fonts/malgun.ttf").get_name()
    rc('font', family=font_name)
    cntput = '0'
    while type(cntput) != int:
        cntput = int(input('그래프에 표시할 단어 갯수를 입력하세요 : '))
        if type(cntput) != int:
            print('숫자를 입력해주세요')
    graph_size_x = 0
    graph_size_y = 0
    print('그래프 크기가 작을 경우 문자가 잘려 나올 수 있습니다.')
    while graph_size_x == 0 or graph_size_y == 0:
        try:
            graph_size_x = int(input('그래프의 X축 크기(cm)를 입력하세요 :'))
            graph_size_y = int(input('그래프의 Y축 크기(cm)를 입력하세요 :'))
        except ValueError:
            print('숫자를 입력해주세요')
    t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    t = t.replace(':','')
    if not exists('C:/kurlycroll/'+t):
        os.mkdir('C:/kurlycroll/'+t)
        print('C:\\kurlycroll\\'+t+' 폴더를 생성했습니다.')
    else:
        print('C:\\kurlycroll\\'+t+' 폴더가 이미 존재합니다.')
            
    pylab.show = lambda: pylab.savefig('C:/kurlycroll/'+t+'/'+str(cnt)+'.jpg')
    rcParams['figure.figsize'] = graph_size_x/2.54, graph_size_y/2.54
    print('그래프는 C:/kurlycroll/'+t+'에 저장됩니다.')
    cnt = 1
    for ko_keys in product_analysis.keys():
        c = product_analysis[ko_keys][0].split()
        ko = nltk.Text(c, name=ko_keys)
        fig = plt.figure()
        plt.title(ko_keys,fontsize=20)
        ko.plot(cntput)
        cnt += 1
    return driver, product_dic


price_dic = {}  
page_list = []
  
def croll():
    driver, product_dic = croll_graph()
    price_dic = {}  
    page_list = []
    
    save_sales = None
    while save_sales != 'Y':
            save_sales = input('리뷰 기반으로 각 상품별 매출그래프를 출력할까요?(Y/N) : ').upper()
            if save_sales == 'N':
                return print('프로그램을 종료합니다.')
            elif save_sales != 'Y':
                print('Y 또는 N 으로 입력해주세요')
                
    print('상품 가격을 조회중입니다. 잠시만 기다려주세요...')
    
    price_list_url = 'http://www.kurly.com/shop/main/index.php'
    price_url = urllib.request.Request(price_list_url)
    price_res = urllib.request.urlopen(price_url).read()
    price_soup = BeautifulSoup(price_res, "lxml")  
    price_notices = price_soup.select('li.dep1')
    for a in price_notices:
        for b in str(a).split('>'):
            if b.find('category=') != -1:
                page_list.append(b[b.find('category=')+9:].replace('"',''))
    
    for c in page_list:
        price_list_url2 = 'http://www.kurly.com/shop/goods/goods_list.php?category='+c
        price_url2 = urllib.request.Request(price_list_url2)
        price_res2 = urllib.request.urlopen(price_url2).read()
        price_soup2 = BeautifulSoup(price_res2, "lxml")  
        price_page = price_soup2.select('a.layout-pagination-button.layout-pagination-last-page')
        price_page_cnt = price_page[0].get('href')[price_page[0].get('href').find('page=')+5:]
        
        for d in range(1,int(price_page_cnt)+1):
            price_list_url3 = 'http://www.kurly.com/shop/goods/goods_list.php?category='+c+'&page='+str(d)    
            price_url3 = urllib.request.Request(price_list_url3)
            price_res3 = urllib.request.urlopen(price_url3).read()
            price_soup3 = BeautifulSoup(price_res3, "lxml")  
            goods_name = price_soup3.select('div ul li a div p.goods-list-item-name')
            goods_price = price_soup3.select('#content div ul li a div p.goods-list-item-price')        
            
            for e,f in zip(goods_name, goods_price):
                if e.get_text(strip=True).find('.goods') != -1:
                    price_dic[e.get_text(strip=True)[:e.get_text(strip=True).find('.goods')]] = f.get_text(strip=True)
                else:
                    price_dic[e.get_text(strip=True)] = f.get_text(strip=True)
            
        
    sales_dic = {}
    for g,h in product_dic.items():
        if g not in price_dic:
            driver.get('http://www.kurly.com/shop/goods/goods_review.php')
            html = driver.page_source
            search = driver.find_element_by_class_name("header-main-search-input")
            search.send_keys(g)
            search.submit()
            time.sleep(2)
            html2 = driver.page_source
            search_soup = BeautifulSoup(html2, "lxml")
            search_name = search_soup.select('p.goods-list-item-name')
            search_price = search_soup.select('p.goods-list-item-price')
            for i,j in zip(search_name, search_price):
                if i.get_text(strip=True).find('.goods') != -1:
                    price_dic[i.get_text(strip=True)[:i.get_text(strip=True).find('.goods')]] = j.get_text(strip=True)
                else:
                    price_dic[i.get_text(strip=True)] = j.get_text(strip=True)
        sales_dic[g] = int(price_dic[g][:price_dic[g].find('원')].replace(',',''))*h[-1]
    driver.quit()    
        
        
        

    df = pd.DataFrame(sales_dic,index=['매출'])
    df = df.T
    df = df.sort_values(by='매출', ascending = False)
    
    font_name = font_manager.FontProperties(fname="c:/Windows/Fonts/malgun.ttf").get_name()
    rc('font', family=font_name)
    
    graph_size_x = 0
    graph_size_y = 0    
    how_many = 0
    print('그래프 크기가 작을 경우 문자가 잘려 나올 수 있습니다.')
    while graph_size_x == 0 or graph_size_y == 0 or how_many == 0:
        try:
            graph_size_x = int(input('그래프의 X축 크기(cm)를 입력하세요 :'))
            graph_size_y = int(input('그래프의 Y축 크기(cm)를 입력하세요 :'))
            how_many = int(input('표시할 매출 상위 제품 갯수를 입력하세요 : '))
        except ValueError:
            print('숫자를 입력해주세요')
            
    print('매출그래프는 C:/kurlycroll/ 에 현재 시각으로 저장됩니다.')
    
    t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    t = t.replace(':','')
    pylab.show = lambda: pylab.savefig('C:/kurlycroll/'+t+'.jpg')
    rcParams['figure.figsize'] = graph_size_x/2.54, graph_size_y/2.54
    df.head(how_many).plot(kind='bar')
    pylab.show()
    
    
    

croll()





'''
진행중 : 리뷰를 통한 각 상품 매출 데이터,
    		"    마켓커리의 시장분류 및 분석과 그래프를 통한 가시화
        1차분류만 되어있는 크롤링 대상을 2차분류까지 확대
	 

문제점 : 페이지를 크롤링 할 수록 dictionary 변수가 커져 점점 크롤링속도가 느려진다.
         간헐적으로 url연결이 끊길때가 있다.
        konlpy 모듈이 완벽하지 않아 무의미한 단어가 많이 출력된다.
        exe 변환시 그래프 출력이 원활하지않음
        그래프를 IPython notebook타입으로 변경시도중 
'''






