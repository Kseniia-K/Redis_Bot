import telebot
import redis

try:
    bot = telebot.TeleBot('7053275253:AAHq5kW7gwOyh4V6hFBmevnGtHYudUsqayg')
    r = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

    def if_user_exists(user_id):
        return r.hexists(f"user:{user_id}", "name")
    
    def age_input(message):
        age = message.text
        user_id = message.from_user.id
        r.hset(f"user:{user_id}", "age", age)
        bot.send_message(message.chat.id, f"Профиль успешно создан! Имя: {r.hget(f'user:{user_id}', 'name')}, Возраст: {age}")

    def name_input(message):
        name = message.text
        user_id = message.from_user.id
        r.hset(f"user:{user_id}", "name", name)
        sent_msg = bot.send_message(message.chat.id, "Сколько вам лет?")
        bot.register_next_step_handler(sent_msg, age_input)

    def change_info(message):
        user_id = message.from_user.id
        try:
            name, age = message.text.split("; ")
            r.hset(f"user:{user_id}", "name", name)
            r.hset(f"user:{user_id}", "age", age)
            bot.send_message(message.chat.id, "Данные профиля успешно обновлены!")
        except ValueError:
            bot.send_message(message.chat.id, "Вы неверно ввели данные, попробуйте ещё раз: /change")

    @bot.message_handler(commands=['start'])
    def handle_start(message):
        bot.send_message(message.chat.id, "Привет! Я ваш телеграм-бот. Чтобы создать профиль введите: /create")

    @bot.message_handler(commands=['create'])
    def create_profile(message):
        user_id = message.from_user.id
        if if_user_exists(user_id):
            bot.send_message(message.chat.id, "Такой профиль уже есть в системе. Чтобы изменить его введите: /change")
        else:
            sent_msg = bot.send_message(message.chat.id, "Как вас зовут?")
            bot.register_next_step_handler(sent_msg, name_input)

    @bot.message_handler(commands=['change'])
    def change_profile(message):
        user_id = message.from_user.id
        if if_user_exists(user_id):
            sent_msg = bot.send_message(message.chat.id, "Введите новое имя и возраст: Имя; возраст")
            bot.register_next_step_handler(sent_msg, change_info)
        else:
            bot.send_message(message.chat.id, "Такого профиля нет в системе. Проверьте введённые данные или создайте новый, введя /create")
    
    @bot.message_handler(commands=['delete'])
    def delete_profile(message):
        user_id = message.from_user.id
        if if_user_exists(user_id):
            r.delete(f"user:{user_id}")
            bot.send_message(message.chat.id, "Профиль успешно удалён!")
        else:
            bot.send_message(message.chat.id, "Такого профиля нет в системе, проверьте введённые данные")

    def admin_permission(message):
        command = message.text
        print(command)
        if command == "/list_all_profiles":
            keys = r.keys("user:*")
            users = {key: r.hgetall(key) for key in keys}
            bot.send_message(message.chat.id, f"Список профилей:\n" + "\n".join([f"{key}: {value}" for key, value in users.items()]))
        elif command == "/delete_all_profiles":
            keys = r.keys("user:*")
            for key in keys:
                r.delete(key)
            bot.send_message(message.chat.id, "Все профили успешно удалены!")
        else:
            bot.send_message(message.chat.id, "Такой команды нет в системе, проверьте введённые данные")

    def passwd(message):
        command = message.text
        if command == "123":
            sent_msg = bot.send_message(message.chat.id, "Чтобы увидеть все профили введите: /list_all_profiles, чтобы удалить все профили введите: /delete_all_profiles):")
            bot.register_next_step_handler(sent_msg, admin_permission)
        else:
            bot.send_message(message.chat.id, "Неверный пароль! Попробуйте ещё раз: /admin")

    @bot.message_handler(commands=['admin'])
    def admin_actions(message):
        sent_msg = bot.send_message(message.chat.id, "Введите пароль администратора:")
        # sent_msg = bot.send_message(message.chat.id, "Чтобы увидеть все профили введите: list profiles, чтобы увдалить все профили введите: delete profiles):")
        # bot.register_next_step_handler(sent_msg, admin_permission)
        bot.register_next_step_handler(sent_msg, passwd)

    bot.polling()
except redis.exceptions.ConnectionError:
    print("Ошибка подключения к Redis.")
except redis.exceptions.TimeoutError:
    print("Превышено время ожидания при работе с Redis.")
except redis.exceptions.AuthenticationError:
    print("Ошибка аутентификации при подключении к Redis.")
except Exception as e:
    print(f"Произошла неизвестная ошибка: {e}")