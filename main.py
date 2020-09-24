# from random import randrange
# import vk_api
# from vk_api.longpoll import VkLongPoll, VkEventType
# from db_adm_pass import vk_token
from vkinder_bot import VKinderBot


if __name__ == '__main__':
    bot = VKinderBot()


# vk = vk_api.VkApi(token=vk_token)
# longpoll = VkLongPoll(vk)



# for event in longpoll.listen():
#     print(event)
#     if event.type == VkEventType.MESSAGE_NEW:
#
#         if event.to_me:
#             request = event.text
#             # bot.write_msg(event.user_id, f"Хай, {event.user_id}")
#
#             if request == "привет":
#                 bot.say_hi(event)
#             elif request == "пока":
#                 bot.say_bye(event)
#             elif request == 'vkinder':
#                 bot.vkinder_init_command(event)
#             elif request == 'повтори':
#                 bot.repeat(event)
#             else:
#                 bot.say_idk(event)