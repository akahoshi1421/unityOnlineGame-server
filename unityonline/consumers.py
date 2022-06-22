from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json
from unityonline.models import FightingRomm, MatchingQueue
import uuid
import random

def myformat_serialize(string):#独自のフォーマットをリスト化
    result = []
    ichiji = ""
    for a in string:
        if a == ",":
            result.append(ichiji)
            ichiji = ""
        else:
            ichiji += a
    return result

def myformat_deserialize(lists):#独自のフォーマットを文字列化
    string = ""
    for b in lists:
        string += str(b)
        string += ","
    return string

class MatchingConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()
    
    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        userUuidJson = json.loads(text_data)
        #{"uuid": "ユーザのuuid(unity側で生成する)"}
        userUuid = userUuidJson["uuid"]
        matchingQueue = MatchingQueue.objects.get(id = 1)
        matchingQueueList = myformat_serialize(matchingQueue.waiting_users)
        
        if len(matchingQueueList) >= 2:
            matchingQueueList.pop(0)
            matchingQueueList.pop(0)
        
        matchingQueueList.append(userUuid)

        matchingQueue.waiting_users = myformat_deserialize(matchingQueueList)
        matchingQueue.save()

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            { 'type': 'sendMessage', 'message': matchingQueueList }
        )
    
    def sendMessage(self, event):
        print(event["message"])
        if len(event["message"]) < 2:
            self.send(text_data=json.dumps({"playerA": "NONE", "playerB": "NONE"}))
        
        else:
            playerA = event["message"][0]#.pop(0)
            playerB = event["message"][1]#.pop(0)
            matchingQueue = MatchingQueue.objects.get(id = 1)

            matchingQueue.waiting_users = myformat_deserialize(event["message"])
            matchingQueue.save()

            self.send(text_data=json.dumps({"playerA": playerA, "playerB": playerB}))
            #{"1": playerAのuuid, "2": playerBのuuid}


class WaitingConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name + "2"
        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()
    
    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )
    
    def receive(self, text_data):
        userUuidJson = json.loads(text_data)#{"uuid": "そのプレイヤーのuuid", "roomuuid": "そのプレイヤーがいる部屋のuuid"}
        userUuid = userUuidJson["uuid"]
        roomUuid = userUuidJson["roomUuid"]

        res = {}

        try:#二人目
            theroom = FightingRomm.objects.get(id = uuid.UUID(roomUuid))
            addedlist = myformat_serialize(theroom.two_players)
            addedlist.append(userUuid)
            theroom.two_players = myformat_deserialize(addedlist)
            theroom.save()
            res["res"] = "OK"
            res["random"] = [random.randint(1, 4) for i in range(0, 10)]#障害物生成アルゴリズム
            #print(res["random"])
        
        except:#一人目
            theroom = FightingRomm(id = uuid.UUID(roomUuid), two_players = "")
            theroom.two_players = myformat_deserialize([userUuid])
            theroom.save()
            res["res"] = "NG"
            res["random"] = []

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            { 'type': 'sendMessage', 'message': res }
        )
    
    def sendMessage(self, event):
        self.send(text_data=json.dumps({"res": event["message"]["res"], "random": event["message"]["random"]}))
        #{"res": "OK", "random": [1,2,3...]}
        
class FightingConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name + "3"
        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()
    
    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )
    
    def receive(self, text_data):
        pos = json.loads(text_data)
        print(pos)
        #{"userid": "ユーザのuuid", "pos": "レーン位置"}
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            { 'type': 'sendMessage', 'message': pos }
        )

    def sendMessage(self, event):
        data = event["message"]
        print("DEBUG!!!" , data)
        self.send(text_data=json.dumps({"userid": data["userid"], "pos": data["pos"]}))
        #{"userid": "そのプレイヤーのuuid", "pos": "そのプレイヤーがいるレーン(1~4で4はゲームオーバーフラグ)"}