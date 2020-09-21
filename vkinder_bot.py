from random import randrange
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from dating_DB import DatingUser
import sqlalchemy as sq
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from db_adm_pass import db_pass, db_admin, vk_token
import psycopg2
import requests





class VKinderBot:
    def __init__(self): #запускаем бота
        self.vk = vk_api.VkApi(token=vk_token)
        self.longpoll = VkLongPoll(self.vk)
        print('bot launched')

        for event in self.longpoll.listen(): #ждём комманд
            if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me:
                    request = event.text

                    if request == "привет":
                        self.say_hi(event)
                    elif request == "пока":
                        self.say_bye(event)
                        # return
                    elif request == 'vkinder': #запуск корневого раздела для знакомств
                        self.vkinder_init_command(event)
                    elif request == 'повтори': #тестовая команда для ожидания ввода пользователя
                        self.repeat(event)
                    else:
                        self.say_idk(event)

    def write_msg(self, user_id, message):
        self.vk.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7), })
    def say_hi(self, event):
        self.write_msg(event.user_id, f"Хай, {event.user_id}")
    def say_bye(self, event):
        self.write_msg(event.user_id, "Пока((")
    def say_idk(self, event):
        self.write_msg(event.user_id, "Не понял вашего ответа...")
    def wait_command(self): #команда для получения следюущего ответа пользователя
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me:
                    request = event.text
                    return request


    def vkinder_init_command(self, event): #корневой раздел сервиса знакомств
        Base = declarative_base()
        engine = sq.create_engine(f'postgresql+psycopg2://{db_admin}:{db_pass}@localhost:5432/vkinder_DB')
        Session = sessionmaker(bind=engine)
        session = Session()
        user = session.query(DatingUser).all()

        if user == []: # если отсутствет инфоормация о пользователе то создаётся запис в БД
            self.add_new_dating_user(event)
        else:
            self.write_msg(event.user_id, "что будем делать?")#переходы из корневого раздела к другим командам
            for event in self.longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW:
                    if event.to_me:
                        request = event.text

                        if request == "новые партнёры":
                            self.find_new_partners(event)
                        elif request == "покажи понравивишихся":
                            self.see_liked(event)
                        elif request == 'покажи чс':
                            self.see_blacklisted(event)
                        elif request == 'обнови информацию':
                            self.update_user_data(event)
                        elif request == 'в начало':
                            self.write_msg(event.user_id, "перешли в начало")
                            return
                        else:
                            self.show_vkinder_commands(event)

    def find_new_partners(self, event): #команда для поиска партнёров пока только на черновике

        # r = requests.get(
        #     'https://api.vk.com/method/users.search',
        #     params={
        #         'access_token': vk_token,
        #         'v': 5.89,
        #
        #     }
        # )
        # r = r.json()
        pass
    def see_liked(self, event):
        pass
    def see_blacklisted(self, event):
        pass
    def update_user_data(self, event):
        pass
    def show_vkinder_commands(self, event):
        self.write_msg(event.user_id, "Список доступных комманд - новые партнёры, покажи понравивишихся, покажи чс, обнови информацию, в начало")

    def add_new_dating_user(self, event): #метод для первоначального добавления пользователя
        Base = declarative_base()
        engine = sq.create_engine(f'postgresql+psycopg2://{db_admin}:{db_pass}@localhost:5432/vkinder_DB')
        Session = sessionmaker(bind=engine)
        session = Session()
        user = session.query(DatingUser).all()
        self.write_msg(event.user_id, 'Необходимо ввести данные для работы бота VKinder')
        vk_id = event.user_id

        r = requests.get(
            'https://api.vk.com/method/users.get',
            params={
                'access_token': vk_token,
                'v': 5.89,
                'user_ids': vk_id,
                'fields': 'bdate,sex, city',
                'name_case': 'Nom'
            }
        )
        r = r.json()
        first_name = r['response'][0]['first_name']
        last_name = r['response'][0]['last_name']
        city_name = r['response'][0]['city']['title']
        city_id = r['response'][0]['city']['id']
        bdate = r['response'][0]['bdate']

        self.write_msg(event.user_id, f'Укажите минимальный возраст для поиска партнёров')
        age_min = self.wait_command()
        print(age_min)

        self.write_msg(event.user_id, f'Укажите максимальный возраст для поиска партнёров')
        age_max = self.wait_command()
        print(age_max)

        user = DatingUser(dating_id=vk_id, first_name=first_name, last_name=last_name, city_name=city_name, city_id=id, bdate=bdate,
                          age_min=age_min, age_max=age_max)
        session.add(user)
        session.commit()

        self.write_msg(event.user_id, f'Пользователь {vk_id} добавлен')

    def repeat(self, event): #тестовый метод
        self.write_msg(event.user_id, "что повторить?")

        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:

                if event.to_me:
                    request = event.text
                    self.write_msg(event.user_id, request)
                    return