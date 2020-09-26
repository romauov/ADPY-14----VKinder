from random import randrange
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from dating_DB import Session, DatingUser, MatchingUser, Photos, BlacklistedUser
from db_adm_pass import vk_token, search_token
import requests
from collections import Counter


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

    def wait_command(self): #метод для получения следующего ответа пользователя
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me:
                    request = event.text
                    return request

    def vkinder_init_command(self, event): #корневой раздел сервиса знакомств

        session = Session()
        user = session.query(DatingUser).all()

        if len(user) == 0: # если отсутствет информация о пользователе то создаётся запись в БД
            self.add_new_dating_user(event)
            return self.vkinder_init_command(event)
        else:
            self.write_msg(event.user_id, "что будем делать?")#переходы из корневого раздела к другим командам
            for event in self.longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW:
                    if event.to_me:
                        request = event.text

                        if request == "новые партнёры":
                            self.search_new_partners(event)
                        elif request == "покажи понравившихся":
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

    def search_new_partners(self, event):
        # получение исходных данных для поиска партнёров
        session = Session()
        user = session.query(DatingUser).all()
        age_min = user[0].age_min
        age_max = user[0].age_max
        city_id = user[0].city_id
        offset = 0
        sex = user[0].partners_sex

        self.show_possible_partners(event, search_token, offset, city_id, sex, age_min, age_max)

    def show_possible_partners(self, event, search_token, offset, city_id, sex, age_min, age_max):
        #метод для отправки запроса для поиска партнёров
        r = self.users_search_request(search_token, offset, city_id, sex, age_min, age_max)

        id_list = []
        for entry in r:
            if entry['can_access_closed'] == True and entry['is_closed'] == False: #возможно первая часть условия лишняя
                set_id = (entry['first_name'], entry['last_name'], entry['id'])
                id_list.append(set_id)
            else:
                continue

        for entry_id in id_list:
            check = self.database_check(entry_id[2])    #проверка на вхождение в имеющиеся БД
            if check == True:
                continue
            else:
                pics = self.userpics_request(search_token, entry_id[2])

                pics_dict = {pic['sizes'][-1]['url'] : pic['likes']['count'] for pic in pics}
                k = Counter(pics_dict)
                top3_pics = k.most_common(3)
                top3_pics_links = [pic[0] for pic in top3_pics]

                self.write_msg(event.user_id, entry_id[0] + ' ' + entry_id[1]) #выводим имя
                elm_link = 'https://vk.com/id' + str(entry_id[2])
                self.write_msg(event.user_id, elm_link) #выводим ссылку
                for pic in top3_pics_links:
                    self.write_msg(event.user_id, pic) #выводим ссылки на топ-3 фотографии

                request = self.wait_command()
                if request == 'yes':
                    self.add_liked(top3_pics, entry_id[2]) #запись в БД понравивишихся
                    self.write_msg(event.user_id, 'ok')
                elif request == 'stop':
                    return
                else:
                    self.add_blocked(entry_id) #запись в БД чёрного списка
                    self.write_msg(event.user_id, 'it happens')

        self.write_msg(event.user_id, 'список окончен, что дальше?')
        request = self.wait_command()
        if request == 'next': #после окончания списка повтор поиска со смещением выборки
            offset += 20
            return self.show_possible_partners(event, search_token, offset, city_id, sex, age_min, age_max)
        elif request == "покажи понравивишихся":
            self.see_liked(event)
        elif request == 'покажи чс':
            self.see_blacklisted(event)
        else:
            self.write_msg(event.user_id, "перешли в начало")
            return

    def userpics_request(self, search_token, elm_id): #запрос информации о фотографиях пользователя

        r = requests.get(
            'https://api.vk.com/method/photos.get',
            params={
                'access_token': {search_token},
                'v': 5.77,
                'owner_id': {elm_id},
                'album_id': 'profile',
                'rev': 0,
                'extended': 1,
                'photos_sizes': 'z'
            }
        )
        return r.json()['response']['items']

    def users_search_request(self, search_token, offset, city_id, sex, age_min, age_max): #запрос информации о пользователе

        r = requests.get(
            'https://api.vk.com/method/users.search',
            params={
                'access_token': {search_token},
                'v': 5.89,
                'sort': 0,
                'offset': {offset},
                'city': {city_id},
                'sex': {sex},
                'status': 6,
                'age_from': {age_min},
                'age_to': {age_max}
            }
        )
        r = r.json()['response']['items']
        return r

    def add_liked(self, top3_pics, matching_id): #метод для записи в БД понравившихся пользователей
        session = Session()
        user = session.query(DatingUser).all()
        id_dater = user[0].dating_id

        r = requests.get(
            'https://api.vk.com/method/users.get',
            params={
                'access_token': vk_token,
                'v': 5.89,
                'user_ids': matching_id,
                'fields': 'bdate, sex',
                'name_case': 'Nom'
            }
        )
        r = r.json()
        first_name = r['response'][0]['first_name']
        last_name = r['response'][0]['last_name']
        try:
            bdate = r['response'][0]['bdate']
        except:
            bdate = 'NA'
        sex = r['response'][0]['sex']

        liked_user = MatchingUser(matching_id=matching_id, first_name=first_name, last_name=last_name, bdate=bdate, id_dater=id_dater, sex=sex)
        session.add(liked_user)
        session.commit()

        for photo in top3_pics:
            pic_link = photo[0]
            pic_likes = photo[1]
            photo = Photos(id_matcher=matching_id, photo_link=pic_link, likes_count=pic_likes)
            session.add(photo)
            session.commit()

    def add_blocked(self, entry_id): #метод для записи в БД чёрного списка
        session = Session()
        user = session.query(DatingUser).all()

        id_dater = user[0].dating_id
        blacklisted_id = entry_id[2]
        first_name = entry_id[0]
        last_name =entry_id[1]

        disliked_iser = BlacklistedUser(blacklisted_id=blacklisted_id, first_name=first_name, last_name=last_name, id_dater=id_dater)
        session.add(disliked_iser)
        session.commit()

    def database_check(self, check_id): #метод для проверки на вхождение в БД
        session = Session()

        liked_users = session.query(MatchingUser).all()
        liked_users_list = [liked_user.matching_id for liked_user in liked_users]

        disliked_users = session.query(BlacklistedUser).all()
        disliked_users_list = [disliked_user.blacklisted_id for disliked_user in disliked_users]

        if check_id in liked_users_list or check_id in disliked_users_list:
            return True
        else:
            return False

    def see_liked(self, event): #вывод из БД понравившихся
        session = Session()
        liked_users = session.query(MatchingUser).all()
        photos = session.query(Photos).all()

        for liked_user in liked_users:
            first_name = liked_user.first_name
            last_name = liked_user.last_name
            id = liked_user.matching_id
            user_info = first_name + ' ' + last_name + ' ' + 'https://vk.com/id' + str(id)
            self.write_msg(event.user_id, user_info)
            for photo in photos:
                if id == photo.id_matcher:
                    self.write_msg(event.user_id, photo.photo_link)

    def see_blacklisted(self, event): #вывод из БД чёрного списка
        session = Session()

        blacklisted_users = session.query(BlacklistedUser).all()
        for user in blacklisted_users:
            first_name = user.first_name
            last_name = user.last_name
            id = user.blacklisted_id
            bl_user = first_name + ' ' + last_name + ' ' + 'https://vk.com/id' + str(id)
            self.write_msg(event.user_id, bl_user)

    def update_user_data(self, event): #метод для обновления информации для поиска
        session = Session()
        user = session.query(DatingUser).all()[0]
        id = user.dating_id

        self.write_msg(event.user_id, f'Укажите минимальный возраст для поиска партнёров')
        age_min = self.wait_command()

        self.write_msg(event.user_id, f'Укажите максимальный возраст для поиска партнёров')
        age_max = self.wait_command()

        self.write_msg(event.user_id, f'Укажите пол партнёров для поиска поиска, м или ж')
        partners_sex = self.wait_command()
        if partners_sex == 'м':
            partners_sex = 2
        elif partners_sex == 'ж':
            partners_sex = 1
        else:
            self.write_msg(event.user_id, f'ничего не понял, спрошу ещё раз')
            return self.update_user_data(event)

        session.query(DatingUser).filter(DatingUser.dating_id == id).update(
            {"age_min": age_min, "age_max": age_max, "partners_sex": partners_sex}
        )
        session.commit()
        self.write_msg(event.user_id, 'информация обновлена')

    def show_vkinder_commands(self, event):
        self.write_msg(event.user_id, "Список доступных комманд - новые партнёры, покажи понравивишихся, покажи чс, обнови информацию, в начало")

    def add_new_dating_user(self, event): #метод для первоначального добавления пользователя

        session = Session()

        self.write_msg(event.user_id, 'Необходимо ввести данные для работы бота VKinder')
        vk_id = event.user_id

        r = requests.get(
            'https://api.vk.com/method/users.get',
            params={
                'access_token': vk_token,
                'v': 5.89,
                'user_ids': vk_id,
                'fields': 'bdate, sex, city',
                'name_case': 'Nom'
            }
        )
        r = r.json()
        first_name = r['response'][0]['first_name']
        last_name = r['response'][0]['last_name']
        city_name = r['response'][0]['city']['title']
        city_id = r['response'][0]['city']['id']
        bdate = r['response'][0]['bdate']
        sex = r['response'][0]['sex']

        self.write_msg(event.user_id, f'Укажите минимальный возраст для поиска партнёров')
        age_min = self.wait_command()
        # print(age_min)

        self.write_msg(event.user_id, f'Укажите максимальный возраст для поиска партнёров')
        age_max = self.wait_command()

        self.write_msg(event.user_id, f'Укажите пол партнёров для поиска поиска, м или ж')
        partners_sex = self.wait_command()
        if partners_sex == 'м':
            partners_sex = 2
        elif partners_sex == 'ж':
            partners_sex = 1
        else:
            self.write_msg(event.user_id, f'ничего не понял, спрошу ещё раз')
            return self.add_new_dating_user(event)

        user = DatingUser(dating_id=vk_id, first_name=first_name, last_name=last_name, city_name=city_name, city_id=city_id, bdate=bdate,
                          age_min=age_min, age_max=age_max, sex=sex, partners_sex=partners_sex)
        session.add(user)
        session.commit()

        self.write_msg(event.user_id, f'Пользователь {vk_id} добавлен')