# coding: utf-8
import pprint
import random
def print_tree(tree):
    pprint.pprint(tree)

#可以输入的类型,输入其他类型字符串都认为没在出牌
card_filter = u'234567890jJqQkKaAwW大小 ,，.．!！;：:；\'\"'
#所有扑克牌字面表示的点数
CARD_DICT = {
u'3':3,u'4':4,u'5':5,u'6':6,u'7':7,u'8':8,u'9':9,u'0':10,
u'j':11,u'q':12,u'k':13,u'a':14,
u'J':11,u'Q':12,u'K':13,u'A':14,
u'2':15,
u'w':16,u'W':17,}#小王大王区分大小写


REVERSE_CARD_DICT = {3:u'3',
4:u'4',
5:u'5',
6:u'6',
7:u'7',
8:u'8',
9:u'9',
10:u'0',
11:u'J',
12:u'Q',
13:u'K',
14:u'A',
15:u'2',
16:u'w',
17:u'W',
}
def card_list_to_str(card_list):
    Len=len(card_list)
    card_str=u''
    for i in range(0,Len):
        c = card_list[i]
        card_str += REVERSE_CARD_DICT[c]
    return card_str
def card_dict_to_str(card_dict):
    Len=len(card_dict)
    card_list = []
    for point in card_dict:
        count = card_dict[point]["count"]
        for i in range(0,count):
            card_list.append(point)

    str = card_list_to_str(card_dict)
    return str

#发牌,返回三个玩家的牌,以及剩下的三张牌
def shuffle_card():
    #所有牌的列表,从这里面随机抽取
    card_54=[]
    for i in range(3,16):
        for cnt in range(4):
            card_54.append(i)
    card_54.append(16)
    card_54.append(17)

    print(card_54)
    player0=[]
    player1=[]
    player2=[]

    #产生随机索引
    for i in range(0,17):
        rand_index = random.randint(0,len(card_54)-1)
        c = card_54[rand_index]
        player0.append(c)
        del card_54[rand_index]

        rand_index = random.randint(0,len(card_54)-1)
        c = card_54[rand_index]
        player1.append(c)
        del card_54[rand_index]

        rand_index = random.randint(0,len(card_54)-1)
        c = card_54[rand_index]
        player2.append(c)
        del card_54[rand_index]

    player0.sort()
    player1.sort()
    player2.sort()
    card_54.sort()
    return player0,player1,player2,card_54

#10,和0都表示10
#单独的1是无效的输入
def input_is_card_string(msg,card_filter):
    global i
    for i in range(len(msg)):
        c = msg[i]
        if card_filter.count(c)==0:#在出牌的字符串里没找到,那么有不属于扑克牌的字符,说明是其他输入
            return False
        '''
        if msg[i]==u'1' and ( not( i<len(msg)-1 and msg[i+1]==u'0') ):#1后面不是0,那么输入并不是10
            print('222')
            return False
        if msg[i]==u'大' and ( not( i<len(msg)-1 and msg[i+1]==u'王') ):#大后面不是王,那么输入并不是大王
            print('333')
            return False
        if msg[i]==u'小' and ( not( i<len(msg)-1 and msg[i+1]==u'王') ):#小后面不是王,那么输入并不是小王
            print('444')
            return False'''
    return True

#剔除无用的字符,整理成统一的格式的字符串,并且排序
def card_point_count_uniform(card_string):
    i=0
    length=len(card_string)
    new = ''
    #跳过非法的扑克牌字符
    while i < length:
        c=card_string[i]
        if c in (CARD_DICT):
           if c==u'j':
               c=u'J'
           elif c==u'q':
               c=u'Q'
           elif c==u'k':
               c=u'K'
           elif c==u'a':
               c=u'A'
           new = new + c
        i+=1
    #整理成排好的扑克牌
    cards={}
    for c in new:
        point=CARD_DICT[c]
        if not cards.has_key(point):
            cards[point] = {'count': 1}
        else:
            cards[point]['count'] = cards[point]['count'] + 1

    return cards


def __get_point_count(cards,point):
    if cards.has_key(point):
        return cards[point]['count']
    return 0

'''
1 火箭：大小王在一起的牌型，即双王牌，此牌型最大，什么牌型都可以打。
2 炸弹：相同点数的四张牌在一起的牌型，比如四条A。除火箭外，它可以打任何牌型，炸弹对炸弹时，要比大小。
3 单支（一手牌）：单张牌，如一支3。
4 对子（一手牌）：相同点数的两张牌在一起的牌型，比如55。
5 三条：相同点数的三张牌在一起的牌型，比如三条4。
6 三带一手：三条 ＋ 一手牌的牌型，比如AAA+9或AAA+77。
7 单顺：五张或更多的连续单支牌组成的牌型，比如45678或345678910JQKA。2和大小王不可以连。
8 双顺：三对或更多的连续对子组成的牌型，比如334455或445566778899。2和大小王不可以连。
9 三顺：二个或更多的连续三条组成的牌型，比如777888或444555666777。2和大小王不可以连。
10 飞机带翅膀：三顺 ＋ 同数量的一手牌，比如777888+3+6或444555666+33+77+88。
11 四带二：四条+两手牌。比如AAAA+7+9或9999+33+55。
'''


def get_card_type(c):
    types = {
        u'火箭':{},

        u'炸弹':{},
        u'四带二':{},

        u'三顺':{},
        u'飞机带翅膀':{},

        u'三条':{},
        u'三带一':{},

        u'双顺':{},
        u'对子':{},

        u'单顺':{},
        u'单支':{},
    }
    erased=[]
    #用来存放王(大王+小王)的个数,4\3\2\1 张牌的数量
    wang=[]
    si=[]
    san=[]
    er=[]
    yi=[]
    #火箭单独判断,否则就把大王或者小王算成单牌
    if __get_point_count(c,16)==1 and __get_point_count(c,17)==1:
        erased.append(16)
        erased.append(17)
        wang.append(16)
        wang.append(17)
        for k in (erased):
            c.pop(k)#有火箭,要单独处理,需要删掉两张牌
    elif __get_point_count(c,16)>=2 or __get_point_count(c,17) >=2:
        return u'错误-王的数量错误'

    for point in c:
        cnt =__get_point_count(c,point)
        if cnt==4:
            si.append(point)
        if cnt==3:#遍历三张同样的牌,提取出来,把他们存到sanshun列表里面
            san.append(point)
        elif cnt==2:
            er.append(point)
        elif cnt==1:#单张数量
            yi.append(point)
        else:
            u'错误-牌的数量错误'

    #火箭
    if len(wang):
        if len(si)==0 and len(san)==0 and len(er)==0 and len(yi)==0:
            return u'火箭'
        elif len(si)==1 and len(san)==0 and len(er)==0 and len(yi)==0:
            return u'四带二-带了双王'
        else:
            return u'错误-火箭不能带其他的牌'
    elif len(si) >= 1:#有炸弹
        if len(si)==1 and len(san)==0 and len(er)==0 and len(yi)==0:
            return u'炸弹'
        elif len(si)==1 and len(er)==2:
            return u'四带二-' + unicode(2) + u'-带了两个对'
        elif len(si)==1 and len(yi)==2:
            return u'四带二-' + unicode(2) + u'-带了两个单'
        elif len(si)==1:
            return u'错误-炸弹不能带除了两个对和两个单以外的牌'
        elif len(si) > 1:
            return u'错误-不能同时出多个炸弹'

    else:#没有炸弹
        #有三张牌并且数量大于等于2,需要判断是否是连续的牌
        if len(san) >= 2:
            san.sort()
            pre=0
            for i in san:#判断是不是连续
               if pre==0:
                  pre=i
               elif pre+1 == i:
                   pre=i
               else:
                   return u"错误-要成为三顺必须是连续的333444..这种"
            #判断带了什么牌
            san_count=len(san)
            er_count=len(er)
            yi_count=len(yi)
            #判断飞机的翅膀对不对
            if er_count==0 and yi_count==0:
                return u'三顺-'+ unicode(san_count) + u'-就是飞机不带翅膀'
            elif san_count==er_count and yi_count==0:
                return u'飞机带翅膀-'+unicode(er_count)+u'-带了对子'
            elif san_count==yi_count and er_count==0:
                return u'飞机带翅膀-'+unicode(yi_count) + u'-带了单子'
            else:
                return u'错误-飞机必须带相同的对子或单子'

        #继续判断是不是三条######################################################
        elif len(san)==1:
            if len(er)==0 and len(yi)==0:
                return u'三条-'
            elif len(er)==1 and len(yi)==0:
                return u'三带一-'+ unicode(len(er)) + u'-带了对子'
            elif len(er)==0 and len(yi)==1:
                return u'三带一-'+ unicode(len(yi)) + u'-带了单子'
            else:
                return u'错误-三带一的数量不对'
        elif len(san)==0:#没有三个的,判断是不是双顺 ###############################################
            if len(er) >=3:
                er.sort()
                pre=0
                for i in er:#判断是不是连续
                   if pre==0:
                      pre=i
                   elif pre+1 == i:
                       pre=i
                   else:
                       return u"错误-要成为双顺必须是连续的334455..这种"

                #判断还有没有剩余牌(双顺不能带牌)
                if len(yi) != 0:
                    return u"错误-双顺不能带牌"
                else:
                    return u'双顺-'+ unicode(len(er))
            elif len(er) == 2:#
                return u'错误-双顺必须是大于等于3个的连续对子,334455..这种'
            elif len(er) == 1:#判断是不是对子,对子不能剩余牌
                if len(yi)==0:
                    return u'对子-'
                else:
                    return u'错误-对子不能带牌'
            elif len(er) == 0:#没有对子######################判断是不是单顺
                if len(yi)>=5:
                    yi.sort()
                    print(yi)
                    pre=0
                    for i in yi:#判断是不是连续
                       if pre==0:
                          pre=i
                       elif pre+1 == i:
                           pre=i
                       else:
                           return u"错误-要成为单顺必须是连续的34567..这种大于等于5个"
                    return u'单顺-' + unicode(len(yi))
                elif len(yi)==1:
                    return u'单支-'
                else:
                    return u'错误-单顺数量就不对'




#比较扑克牌大小

#cards1=[5:{'count':2}, q:{'count':3}]
def compare_cards(cards1,cards2):
    '''比较两手牌的大小,当然,类型要匹配才行'''
    type1=get_card_type(cards1)
    type2=get_card_type(cards2)
    if type1[:2]==u'错误':
         return u'错误-错误的出牌:' + type1
    if type2[:2]==u'错误':
        return u'错误-错误的出牌:'  + type2

    if type1==u'火箭':#最大牌
        return 1
    if type2==u'火箭':
        return -1

    #炸弹比其他类型都大
    if type1==u'炸弹' and type2 != u'炸弹':
        return 1
    if type1!=u'炸弹' and type2 ==u'炸弹':
        return -1

    #都是炸弹比较大小
    if type1==u'炸弹' and type2 == u'炸弹':
        p1=0
        p2=0
        for point in cards1:
            p1=point
            break
        for point in cards2:
            p2=point
            break
        if p1<p2:
            return -1
        if p1>p2:
            return 1
        else:
            return 0

    if type1 != type2:
        return u'错误-不一样的类型 ' + type1 + ' ' +  type2

    big_type1=type1[:type1.find(u'-')]
    big_type2=type1[:type1.find(u'-')]

    #用来比较的值
    point1 = 0
    point2 = 0
    if big_type1 == u'四带二':#寻找4张牌的值
        for point in cards1:
            cnt =__get_point_count(cards1,point)
            if cnt==4:
                point1=point
                break
        for point in cards2:
            cnt =__get_point_count(cards2,point)
            if cnt==4:
                point2=point
                break
    elif big_type1==u'飞机带翅膀' or big_type1==u'三顺' :#寻找飞机333的最小值
        point1=100
        point2=100
        for point in cards1:
            cnt =__get_point_count(cards1,point)
            if cnt==3:
                if point < point1:
                    point1 = point
        for point in cards2:
            cnt =__get_point_count(cards2,point)
            if cnt==3:
                if point < point2:
                    point2 = point

    elif big_type1==u'三条' or big_type1==u'三带一':
        for point in cards1:
            cnt =__get_point_count(cards1,point)
            if cnt==3:
                point1=point
                break
        for point in cards2:
            cnt =__get_point_count(cards2,point)
            if cnt==3:
                point2=point
                break
    elif big_type1==u'双顺':
        point1=100
        point2=100
        for point in cards1:
            cnt =__get_point_count(cards1,point)
            if cnt==2:
                if point < point1:
                    point1 = point
        for point in cards2:
            cnt =__get_point_count(cards2,point)
            if cnt==2:
                if point < point2:
                    point2 = point
    elif big_type1==u'对子':
        for point in cards1:
            point1=point
            break
        for point in cards2:
            point2=point
            break
    elif big_type1==u'单顺':#遍历单顺,寻找最小的值
        point1=100
        point2=100
        for point in cards1:
            if point < point1:
                point1 = point
        for point in cards2:
            if point < point2:
                point2 = point
    elif big_type1==u'单支':
        for point in cards1:
            point1 = point
        for point in cards2:
            point2 = point

    if point1 < point2:
        return -1
    elif point1 == point2:
        return 0
    elif point1 > point2:
        return  1

def card_list_to_dict(list):
         cards={}
         for point in list:
            if not cards.has_key(point):
                cards[point] = {'count': 1}
            else:
                cards[point]['count'] = cards[point]['count'] + 1
         return cards
if __name__ == '__main__':
    p0,p1,p2,left = shuffle_card()

    print(p0,card_list_to_str(p0))
    print(p1,card_list_to_str(p1))
    print(p2,card_list_to_str(p2))
    print(left,card_list_to_str(left))

    print(card_list_to_dict(p0))

    '''
    cards=[u'Ww',u'8888',u'888899',u'888899aa',u'8888jq',u'88',u'889900',u'999',u'999Q',u'999aa',u'999jk',u'999jjkk',u'34567',u'4455667788',u'555666777']
    Len = len(cards)
    for i in range(Len):
        c = cards[i]
        print(c)
        if input_is_card_string(c,card_filter):
            c=card_point_count_uniform(c)
            print(get_card_type(c))
    '''
    print('-----------')
    cards_str1 = '8888'
    cards_str2 = '888889'
    print(input_is_card_string(cards_str1,card_filter))
    print(input_is_card_string(cards_str2,card_filter))
    cards1 = card_point_count_uniform(cards_str1)
    cards2 = card_point_count_uniform(cards_str2)
    print(get_card_type(cards2))
    print(compare_cards(cards1,cards2))



