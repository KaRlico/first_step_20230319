def create_url():
    import time
    from selenium import webdriver
    from bs4 import BeautifulSoup
    import re
    print('마켓컬리 리뷰 크롤링 프로그램을 시작합니다.','\n')
    print('URL값을 가져오는 중입니다. 잠시만 기다려주세요...','\n')
    driver = webdriver.PhantomJS(executable_path='C:/Users/stu/Downloads/phantomjs-2.1.1-windows/phantomjs-2.1.1-windows/bin/phantomjs.exe') #팬텀JS 위치지정하기)
    driver.implicitly_wait(3)    
    driver.get('http://www.kurly.com/shop/goods/goods_review.php') #url로 들어가기
    
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    driver.quit()
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
    return div1_dic


def select_url():
    from bs4 import BeautifulSoup
    #검색할 값 지정 
    put = 0
    div1_dic = create_url()
    for i in div1_dic.keys():
        print(i)
    while put not in div1_dic:
        put = input('크롤링 할 대상을 목록에서 선택해주세요(전체일경우 전체 라고 입력해주세요) : ')
        if put == '전체':
            break
        if put not in div1_dic:
            print('대상이 목록에 없습니다. 띄어쓰기 혹은 맞춤법을 확인해주세요','\n')
    return put,div1_dic







def croll_url():
    #크롤링 시작
    from bs4 import BeautifulSoup
    from konlpy.tag import Twitter; t = Twitter()
    import urllib.request
    import re
    product_dic = {}
    product_analysis = {}
    put, div1_dic = select_url()
    print(put+'에 대해서 크롤링을 시작합니다.','\n')
    if put == '전체':
        list_url = 'http://www.kurly.com/shop/goods/goods_review.php'
    else:
        list_url = 'http://www.kurly.com/shop/goods/goods_review.php?skey=all&cate[0]='+div1_dic[put]+'&sort=1&page_num=20&page=1'
    url = urllib.request.Request(list_url)
    res = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(res,'html.parser')
    page = soup.select_one('a.layout-pagination-button.layout-pagination-last-page')
    if page == None:
        return print('리뷰가 없습니다.')
    else:
        page = page.get('href')[page.get('href').find('page=')+5:]
    
    print(put+'의 리뷰 페이지는 총 '+page_cnt+' 페이지 입니다.','\n')
    select_page = 0
    while select_page == 0 or select_page not in range(1,int(page_cnt)+1):
        select_page = int(input('검색할 페이지 수를 설정하세요(1 ~'+page_cnt+') : '))
        if select_page == 0 or select_page > int(page_cnt):
            print('검색할 페이지가 최대페이지보다 크거나 0입니다.','\n')
    cnt = 0        
    for page in range(1,select_page+1):
        list_url2 = 'http://www.kurly.com/shop/goods/goods_review.php?skey=all&cate[0]='+div1_dic[put]+'&sort=1&page_num=20&page='+str(page)
        url2 = urllib.request.Request(list_url2)
        res2 = urllib.request.urlopen(url2).read()
        soup2 = BeautifulSoup(res,'html.parser')
        product = soup2.findAll('td',{'class':'thumb'}) # 리뷰 상품명
        review1 = soup2.findAll('td',{'class':'txt_title'}) # 리뷰 제목
        review2 = soup2.findAll('div',{'width':'100%'}) # 리뷰 본문
        review_like = soup2.findAll('span',{'class':'review-like-cnt'}) # 리뷰 좋아요
        review_hit = soup2.findAll('span',{'class':'review-hit-cnt'}) # 리뷰 조회수 
        cnt += 1
    
        for pro,rev1,rev2,revlike,revhit in zip(product,review1,review2,review_like,review_hit): # put 제품에 대해 크롤링해서 product_dic에 dict형식으로 집어넣음 value index 0번이 리뷰제목+리뷰본문, 1번이 좋아요, 2번이 조회수 
            if pro.get_text(strip=True) not in product_dic:
                product_dic[pro.get_text(strip=True)] = (rev1.get_text(strip=True), rev2.get_text(strip=True)), int(revlike.get_text(strip=True)), int(revhit.get_text(strip=True))
            else:
                product_dic[pro.get_text(strip=True)] = product_dic[pro.get_text(strip=True)][0] + (rev1.get_text(strip=True), rev2.get_text(strip=True)), product_dic[pro.get_text(strip=True)][-2] + int(revlike.get_text(strip=True)), product_dic[pro.get_text(strip=True)][-1] + int(revhit.get_text(strip=True))
        
        for pro_name in product_dic.keys():
            for pro_review in product_dic[pro_name][0]:
                a = t.pos(pro_review, norm=True, stem=True)
                for i in a:
                    if i[1] == 'Josa' or i[1] == 'Punctuation':
                        continue
                    else:
                        if pro_name not in product_analysis:
                            product_analysis[pro_name] = i[0]
                        else:
                            product_analysis[pro_name] = product_analysis[pro_name]+' '+i[0]
        
    print(str(cnt)+'페이지에 대해 크롤링을 완료하였습니다.','\n')
    
    return product_dic, product_analysis


def croll_return():
    import os
    from os.path import exists
    try:
        product_dic, product_analysis = croll_url()
    except TypeError:
        return 
    put = None
    while put != 'Y':
        put = input('크롤링한 결과를 원본 그대로 보시겠습니까?(Y/N) : ').upper()
        if put == 'N':
            break
        elif put != 'Y':
            print('Y 또는 N 으로 입력해주세요')
        
    if put == 'Y':
        print('원본 결과는 txt 파일로 저장됩니다.','\n')
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
                elif put != 'Y':
                    print('Y 또는 N 으로 입력해주세요')
            if same_file == 'Y':
                print('파일을 덮어씌웁니다.')
                with open('C:/kurlycroll/'+file+'.txt', 'w') as file :
                    for i,j in product_dic.items():
                        file.write('product_name = '+i+'\n') # 제품명
                        cnt = 0
                        for k in j[0]: 
                            cnt += 1
                            if cnt % 2 == 0:
                                file.write(k+'\n\n')
                            else:
                                file.write('리뷰제목 : '+k+'\n')
    
                        for v in range(len(j[1:])):    
                            if v % 2 == 0:
                                data = '좋아요 계 '+str(v)+' '
                                file.write(data)
                            else:
                                data = '조회수 계 '+str(v)+' '
                                file.write(data)
                        file.write('리뷰갯수 '+str(int(cnt/2))+'\n\n\n')
                print('파일을 생성하였습니다.')
                        
        else:
            print('text를 생성합니다.')
            with open('C:/kurlycroll/'+file+'.txt', 'w') as file :
                for i,j in product_dic.items():
                    file.write('product_name = '+i+'\n') # 제품명
                    cnt = 0
                    for k in j[0]: 
                        cnt += 1
                        if cnt % 2 == 0:
                            file.write(k+'\n\n')
                        else:
                            file.write('리뷰제목 : '+k+'\n')

                    for v in range(len(j[1:])):    
                        if v % 2 == 0:
                            data = '좋아요 계 '+str(v)+' '
                            file.write(data)
                        else:
                            data = '조회수 계 '+str(v)+' '
                            file.write(data)
                    file.write('리뷰갯수 '+str(int(cnt/2))+'\n\n\n')   
            print('파일을 생성하였습니다.')
            
            
            
        
        
        
        
    #크롤링 페이지 수, 리뷰 갯수, 
        



'''
import time 
from selenium import webdriver 
from selenium.webdriver.common.keys import Keys 
binary = 'C:/Users/jo/Downloads/chromedriver_win32/chromedriver.exe' 
browser = webdriver.Chrome(binary) 
browser.get('http://google.co.kr') 
search = browser.find_element_by_name('a') 
search.send_keys('google') 
search.send_keys(Keys.RETURN) 
time.sleep(5) 
browser.quit()
'''