#!/usr/bin/env python
# coding: utf-8

from wxbot import *
from card import *
from card_ext import *
def on_char_room_msg(type,msg):
    print(msg)

room_status = 0 #0,什么都不做,1,斗地主状态
secret_code_start=u'斗地主';
secret_code_over=u'结束斗地主';

#游戏状态
class GameRoom():
    def __init__(self):
        self.bot = None
        #房间状态
        self.room_status = 0 #0,什么都不做,1,斗地主叫地主状态,2,出牌状态
        #游戏状态
        self.game_status = 0 #0,准备进入斗地主状态,1,正在斗地主
        self.cmd_game_start = u'开局'
        self.cmd_game_end = u'结束'

        self.room_id = 0
        self.owner_id = 0
        self.owner_name = 0

        #######################重新发牌之后需要复原这几个的值
        self.curr_call_dizhu_max_score = 0#当前叫地主的最高分
        self.curr_call_dizhu_max_score_user_serial=0
        self.new_round_putcard_serial = 0#重新发牌之后最先叫牌的用户,这个不需要清空

        self.last_putcards = None   #前面人出的牌(也可能是自己出的,然后其他人不出,接下来仍然是自己出牌
        self.last_putcards_player_serial = None#前面出牌人的编号,0,1,2

        self.curr_putcard_serial = 0#当前该哪个玩家出牌了,第一个加入的人先叫地主!



        #game_status == 0,准备进入斗地主状态
        self.prepared_person_number = 0#准备好进入游戏的人数

        #如果什么都不做,将在countdown为0时候,退出游戏状态
        self.wait_countdown = 100000
        self.last_game_active_time = int(time.time())
        self.players = {}

    def CreateRoom(self,bot,room_id,uid,name):
        self.bot = bot
        self.room_id = room_id
        self.owner_id = uid
        self.owner_name = name
        self.room_status = 1;

    def DestroyRoom(self,bot,uid):
        if self.owner_id == uid:
            self.__init__()
            return True

    def system_destroy_room(self):
        self.__init__()
    #uid,name是调用者的id 和名字
    def __join_game(self,uid,name):
        if not self.players.has_key(uid):
            number = len(self.players)#编号
            self.players[uid] = { "uid":uid,"name":name,'number':number,'title':'' }

    #uid是调用者的uid,只有第一个进入的才能解散游戏,他离开,游戏这一对局就结束
    def __leave_game(self,uid):
        if not self.players.has_key(uid):
            return
        if self.players[uid]['number'] == 0:
            self.__init__()
        else:
            self.players.pop(uid)

    def send_room_msg(self,msg,gid):
        self.bot.send_msg_by_uid( u'[' + msg + u']',gid)

    def send_personal_msg(self,msg,uid):
        self.bot.send_msg_by_uid(u'[' + msg + u']',uid)

    def IsPlayerInRoomByUid(self,uid):
        if not self.players.has_key(uid):
            return  False
        return True

    #根据玩家的序号获取到玩家,按照加入进来的书序,编号为0,1,2..
    def GetPlayerBySerial(self,number):
        for playerid in self.players:
            player = self.players[playerid]
            player_number = player['number']
            if player_number == number:
                return player
        return None
    #根据玩家id获取到玩家
    def get_player_by_uid(self,uid):
        for playerid in self.players:
            player = self.players[playerid]
            player_uid = player['uid']
            if player_uid == uid:
                return player
        return None

    #负责发牌到每个人手里
    def DispatchCards(self,gid):
         #开始发牌
        card_dict0,card_dict1,card_dict2,card_dict_left = ShuffleCard()
        self.left_card_for_dizhu = card_dict_left #保存下来,留给地主

        card_dicts=[card_dict0,card_dict1,card_dict2]
        flag = False
        for playerid in self.players:
            player = self.players[playerid]
            name = player['name']
            card_dict = card_dicts[player['number']]
            player['usercard_dict'] = card_dict
            card_str= CardDictToStr(card_dict)
            msg = u'玩家'+name + u'牌:' + card_str
            if flag:
                self.send_room_msg(msg,gid)
            else:
                self.send_personal_msg(msg,playerid)

    #选出了地主之后
    def ChooseOutDizhu(self):
        dizhu = self.GetPlayerBySerial(self.curr_putcard_serial % 3)
        dizhu['title']=u'地主'
        nongmin = self.GetPlayerBySerial( (self.curr_putcard_serial+1) % 3)
        nongmin['title']=u'农民1'
        nongmin = self.GetPlayerBySerial( (self.curr_putcard_serial+2) % 3)
        nongmin['title']=u'农民2'
        left_card_for_dizhu= CardDictToStr(self.left_card_for_dizhu)

        #把剩余牌交给地主手里
        for point in self.left_card_for_dizhu:
            if dizhu['usercard_dict'].has_key(point):
                dizhu['usercard_dict'][point]["count"] +=1
            else:
                dizhu['usercard_dict'][point] = {"count":1}

    def RoomHandleMessage(self,name,uid,gid,content):
        if self.game_status == 0:
            if not self.IsPlayerInRoomByUid(uid):#没满,但不在房间里,需要加入
                if content == self.cmd_game_start:#开局
                    self.__join_game(uid,name)
                    self.send_room_msg(name + u'加入了斗地主房间,还差' + unicode(3 - len(self.players)) + u'个人',gid)
                    if len(self.players) == 3:
                        self.game_status = 1 #加入后人满了,可以叫发牌,然后叫地主
                        self.DispatchCards(gid)
                        #新一局的第一个玩家序号
                        self.curr_putcard_serial = self.new_round_putcard_serial
                        first_call_dizhu_player = self.GetPlayerBySerial(0)#第一次开局成功是第一个加入的人先叫地主
                        name = first_call_dizhu_player['name']
                        uid = first_call_dizhu_player['uid']
                        self.send_personal_msg(u'发牌完毕,' + name + u'请先叫地主.',uid)
                else:
                    #self.send_room_msg(u'[别人正在准备斗地主,先等等]',gid)
                    print(u'[别人正在准备斗地主,先等等]')
            else:#m没满,但是在房间里,需要等其他人加入才行
                #self.send_room_msg(u'[你们都快点加入啊]',gid)
                 print(u'你们都快点加入啊')
        elif self.game_status == 1:
            if(not self.IsPlayerInRoomByUid(uid)):#不在房间里
                #self.send_room_msg(u'[别人正在准备斗地主,先等等]',gid)
                print(u'[别人正在准备斗地主,先等等]')
            elif self.players[uid]['number'] == self.curr_putcard_serial:
                if content != u'1分' and content !=u'2分' and content !=u'3分' and content !=u'不叫':
                    self.send_personal_msg( name + u'请回答:1分,2分,3分或者不叫',uid)
                    return

                score = 0
                if content == u'1分':
                    score=1
                elif content == u'2分':
                    score=2
                elif content ==u'3分':
                    score=3
                elif content==u'不叫':
                    score=0

                #self.new_round_putcard_serial + 2 是每次叫地主最后一个人的序号
                if self.curr_putcard_serial != (self.new_round_putcard_serial + 2)%3:
                    if score==0:#不叫
                        self.curr_putcard_serial+=1
                        self.curr_putcard_serial %= 3
                        return
                    elif score <= self.curr_call_dizhu_max_score :
                        self.send_personal_msg( name + u',要么不叫,要么请喊比'+ unicode(self.curr_call_dizhu_max_score)+u'高的分',uid)
                        return
                    elif score == 3:#确定了地主
                        #self.send_personal_msg(card_str,playerid)
                        self.ChooseOutDizhu()
                        dizhu = self.GetPlayerBySerial(self.curr_putcard_serial % 3)
                        msg = dizhu['name'] + u'[' + dizhu['title'] + u']的三张牌是:' + CardDictToStr(self.left_card_for_dizhu)
                        self.send_room_msg(msg,gid)
                        self.game_status = 2
                        return
                    else:
                        self.curr_call_dizhu_max_score = score#记录当前最高分
                        self.curr_call_dizhu_max_score_user_serial = self.curr_putcard_serial#记录当前出最高分的人的序号
                        self.curr_putcard_serial+=1
                        self.curr_putcard_serial %= 3
                        return
                else:#最后一个人叫了,如果不叫,判断之前有人叫了么,没有就重新发牌
                    if self.curr_call_dizhu_max_score == 0:#没人叫地主,重新发牌
                        self.game_status = 1
                        self.DispatchCards(gid)
                        self.new_round_putcard_serial += 1#修改下一局的出牌顺序
                        self.new_round_putcard_serial %=3
                        next_first_player = self.GetPlayerBySerial(self.new_round_putcard_serial)
                         #修改出牌人顺序
                        self.curr_putcard_serial = self.new_round_putcard_serial
                        self.send_room_msg(u'上一局没人叫地主,重新发牌了,这次轮到' + next_first_player['name']+u'先叫地主',gid)
                    else:#确定地主,然后翻出地主的牌
                        if score < self.curr_call_dizhu_max_score:
                            self.curr_putcard_serial= self.curr_call_dizhu_max_score_user_serial#地主为最高分的人,接下来第一个出牌
                        self.ChooseOutDizhu()
                        dizhu = self.GetPlayerBySerial(self.curr_putcard_serial % 3)
                        msg = dizhu['name'] + u'[' + dizhu['title'] + u']的三张牌是:' + CardDictToStr(self.left_card_for_dizhu)
                        self.send_room_msg(msg,gid)
                        self.game_status = 2
                        return
            else:
                self.send_room_msg( name + u',还没轮到你叫地主呢..请等等',gid)
                self.last_game_active_time = int(time.time())
        elif self.game_status == 2:
            if(not self.players.has_key(uid)):#不在房间里
                self.send_room_msg(u'[别人正在准备斗地主,先等等]',gid)
            elif content == self.cmd_game_end:#结束
                self.__leave_game(uid);
                self.send_room_msg(name + u'离开了斗地主房间,还差' + unicode(3 - len(self.players)) + u'个人,大家快加入',gid)
                self.game_status = 0;#人不够了..
            else:
                #正常的进入游戏的出牌逻辑
                self.RoomHandlePlayingCard(uid,name,content,gid)
                self.last_game_active_time = int(time.time())

    def is_valid_card(self,cards):
        print('')

    def RoomHandlePlayingCard(self,uid,name,content,gid):
        print(content)
        #当前该出牌的人
        curr_output_player=self.GetPlayerBySerial(self.curr_putcard_serial)
        is_content_cards = InputIsCardString(content)

        #其他人都不出,自己再次出牌,不需要比较,直接出牌就是了
        if not self.last_putcards_player_serial:#地主不能不出牌啊
            self_again = True
        else:
            self_again = (self.last_putcards_player_serial == self.curr_putcard_serial)
        if self.players[uid]['number'] != self.curr_putcard_serial:#没到出牌顺序呢
            self.send_room_msg(name + u'还没轮到你出牌呢,该轮到' + curr_output_player['name'] + u'出牌.',gid)
            return
        elif content == u'不出' or content == u'bc' or content == u'b':
            if self_again:
                self.send_room_msg(curr_output_player['name'] + u'上次是你出的牌,而其他人都不出,该你出牌了' + name + u'.',gid)
                return
            else:
                self.curr_putcard_serial += 1
                self.curr_putcard_serial %= 3
                return
        elif not is_content_cards:
            self.send_room_msg(curr_output_player['name'] + u'请出牌',gid)
            return


        #玩家出牌的列表dict
        cards_output_dict = CardStrToCardDict(content)

        #检测是不是合理的牌,555+67这种不正确的直接提示错误的出牌
        type=get_card_type(cards_output_dict)
        if type[:2]==u'错误':
            self.send_room_msg(name + u'你出的牌:' + type,gid)
            return
        #玩家拥有的牌数,list
        player_own_card_dict = self.players[uid]['usercard_dict']

        print_tree(player_own_card_dict)

        print_tree(cards_output_dict)

        #检查牌是不是自己有的牌
        is_card_engouth = CheckCardEnough(player_own_card_dict,cards_output_dict)
        if not is_card_engouth:
            self.send_room_msg(name + u'你出的牌里有些是自己没有的牌..',gid)
            return
        #出的是自己有的牌


        if self.last_putcards and (not self_again):#有上一家出的牌,并且不是自己出的,才需要比较
            com_result = compare_cards(cards_output_dict,self.last_putcards)
            if com_result != -1 and com_result != 0 and com_result != 1:
                self.send_room_msg(name + u'你出的牌:' + com_result,gid)
            if com_result <= 0: #牌没有上一家出的大
                str=CardDictToStr(self.last_putcards)
                self.send_room_msg(name + u'你出的牌管不起..' + str,gid)
            else:
                #扣牌
                MinusCard(player_own_card_dict,cards_output_dict)
                #剩余的牌,私聊发给玩家
                left_str = CardDictToStr(player_own_card_dict)
                self.send_personal_msg(left_str,uid)

                #检查完是否牌都出完了
                over = True
                for c in player_own_card_dict:
                    data = player_own_card_dict[c]
                    if data['count'] > 0:
                        over = False
                        break
                if over:
                    self.send_room_msg(name + self.players[uid]['title'] + u'获胜,开始新局',gid)
                    #重新发牌开始新局
                    self.game_status = 1
                    self.DispatchCards(gid)
                    self.new_round_putcard_serial += 1#修改下一局的出牌顺序
                    self.new_round_putcard_serial %= 3
                    #修改出牌人顺序
                    self.curr_putcard_serial = self.new_round_putcard_serial
                    self.last_putcards_player_serial = None
                    self.last_putcards = None
                    next_first_player = self.GetPlayerBySerial(self.curr_putcard_serial)
                    self.send_room_msg(next_first_player['name']+u'请先叫地主',gid)
                else:
                     #剩余的牌,私聊发给玩家
                    left_str = CardDictToStr(player_own_card_dict)
                    self.send_personal_msg(left_str,uid)
                    self.curr_putcard_serial += 1
                    self.curr_putcard_serial %= 3

        else: #第一次出牌,或者其他人都不出牌,又轮到自己了
            self.last_putcards = cards_output_dict
            self.last_putcards_player_serial = curr_output_player['number']
            #扣牌
            MinusCard(player_own_card_dict,cards_output_dict)
            #检查完是否牌都出完了
            over = True
            for c in player_own_card_dict:
                data = player_own_card_dict[c]
                if data['count'] > 0:
                    over = False
                    break

            if over:
                self.send_room_msg(name + self.players[uid]['title'] + u'获胜,开始新局',gid)
                #重新发牌开始新局
                self.game_status = 1
                self.DispatchCards(gid)
                self.new_round_putcard_serial += 1#修改下一局的出牌顺序
                self.new_round_putcard_serial %= 3
                #修改出牌人顺序
                self.curr_putcard_serial = self.new_round_putcard_serial
                self.last_putcards_player_serial = None
                self.last_putcards = None
                next_first_player = self.GetPlayerBySerial(self.curr_putcard_serial)
                self.send_room_msg(next_first_player['name']+u'请先叫地主',gid)
            else:
                #剩余的牌,私聊发给玩家
                left_str = CardDictToStr(player_own_card_dict)
                self.curr_putcard_serial += 1
                self.curr_putcard_serial %= 3


def dic_set(dic,key,value):
     if not dic.has_key(key):
       dic[key] = {}
     dic[key] = value

def dic_get(dic,key):
    if dic.has_key(key):
        return dic[key]
    return None

class MyWXBot(WXBot):
    def game_tip_not_friend(self,name,uid,gid):
         self.send_msg_by_uid( name + u'你好,请添加群主为好友才能继续..',gid);

    def handle_msg_all(self, msg):
        print_tree(msg)
        #自己发送消息,也有可能发送到群聊
        '''if msg['msg_type_id'] == 1:
            if msg['to_user_id'][:2]==u'@@':
                on_char_room_msg(1,msg)
       '''
        if  msg['msg_type_id'] == 1 or msg['msg_type_id'] == 3: #群消息
            print("群消息....\n")

            #group_id = msg['user']['id'];
            #print('group id ',group_id);

            if msg['msg_type_id'] == 1:
                group_id = msg['to_user_id']
                uid = msg['user']['id']#发送者id
                name = msg['user']['name']#发送者name
                data =  msg['content']['data'];
            else:
                group_id = msg['user']['id'];
                uid = msg['content']['user']['id']#发送者id
                name = msg['content']['user']['name']#发送者name
                data =  msg['content']['data'];
            print(group_id,uid,name,data)
            is_friend = 0;
            #是不是自己好友,自己算是自己的好友.
            if u'contact' != self.get_user_type(uid):
                #self.send_msg_by_uid( msg['content']['user']['name'] + u'你好,请添加群主为好友才能继续..',msg['user']['id']);
                if self.my_account['UserName'] == uid:
                    is_friend = 1
                    #self.send_msg_by_uid('自己发送的消息',uid)
                else:
                    is_friend = 0;
            else:
                is_friend = 1;

            room_inst = None;
            if self.game_rooms.has_key(group_id):
                room_inst = self.game_rooms[group_id]
            #创建房间和销毁房间
            if data == secret_code_start:
                if is_friend == 0:
                    self.game_tip_not_friend(name,uid,group_id)
                    return

                if not self.game_rooms.has_key(group_id):
                    room_inst = GameRoom()
                    room_inst.CreateRoom(self,group_id,uid,name)
                    dic_set(self.game_rooms,group_id,room_inst)

                    self.send_msg_by_uid(name + u'每个群暂时只支持一个斗地主房间'
                                                u'创建者输入"斗地主"创建房间\n'
                                                u'创建者输入"结束斗地主"销毁房间\n'
                                                u'输入"开局"加入房间.\n'
                                                u'一局结束后自动开始新局并发牌,叫地主的顺序后延'
                                                u'234567890j(J)q(Q)k(K)a(A)\n'
                                                u'0,表示10,W表示大王,w表示小王\n'
                                                u'叫地主的时候输入"1","2","3"表示分数,或者"b"表示"不叫"\n'
                                                u'创建了斗地主房间,大家快来加入!\n'
                                                u'',group_id);
                    return
            elif data == secret_code_over:
                 if is_friend == 0:
                    self.game_tip_not_friend(name,uid,group_id)
                    return

                 if self.game_rooms.has_key(group_id):
                    room_inst = self.game_rooms[group_id]
                    succ = room_inst.DestroyRoom(self,uid)
                    if succ:
                        del self.game_rooms[group_id]
                        #self.game_rooms = None
                        room_inst = None
                 return


            #如果在房间里,就把消息交给房间去处理
            if room_inst:
                room_inst.RoomHandleMessage(name,uid,group_id,data)
                return
            else:
                return





            if msg['content']['data'] ==  self.cmd_new_game:
                self.send_msg_by_uid(msg['content']['user']['name'] + u'发起了新的斗地主..',group_id);
        elif msg['msg_type_id'] == 4: #联系人消息(被对方删除自己仍然是好友消息类型,如果自己删除,如果把对方删了就不是好友消息类型)
            print("好友消息....\n")
            if msg['content']['type'] == 12:#未加为好友的消息
                print(msg['content']['data'])
                print(msg['user']['name'],u'请添加群主为好友才能继续..')
                #需要提示消息到群里,让他加为好友才能继续
                #self.send_msg_by_uid( msg['user']['name'] + u'请添加群主为好友才能继续..',msg['content']['user']['id']);


        print('+++++++++++++++++\n\n\n\n');

        if msg['msg_type_id'] == 1 and msg['content']['type'] == 0:
            self.send_msg_by_uid(u'hi', msg['user']['id'])

    def schedule(self):
        #self.send_msg(u'张三', u'测试')
        cur_time = int(time.time())
        '''for room in self.game_rooms:
            if cur_time - room.last_game_active_time  > 100000:
                room.system_destroy_room()
        time.sleep(1000)
        '''
        #self.send_msg_by_uid('自己发送的消息',self.my_account['UserName'])


def main():
    bot = MyWXBot()
    bot.DEBUG = True
    bot.conf['qr'] = 'png'
    bot.game_rooms = {};#用gid作为索引
    bot.run()


if __name__ == '__main__':
    main()
