import telebot
import sqlite3

token = '6233769171:AAHhzew8x6k2SgdbGpfKrqvZXQhcc7WslKg'
bot = telebot.TeleBot(token)
chat_id = '-1001904061097'
info = {'user_id': 0, 'user_name': '', 'mention': '', 'text': '', 'price': '', 'coment': '-', 'status': '', 'photo_id': '-', 'translations': {}}
translat = {}
YOUR_BOT_USERNAME = 'NnPyBot'
YOUR_CHANNEL_USERNAME = 'tapsyrmachannel'

conn = sqlite3.connect('db/database.sqlite', check_same_thread=False)
cursor = conn.cursor()

def db_table_val(id: int, user_id: str, username: str, message_id: str):
	cursor.execute('INSERT INTO users (user_id, username, message_id) VALUES (?, ?, ?)', (user_id, username, message_id))
	conn.commit()

@bot.message_handler(func=lambda message: message.text in ['🇺🇸 English', '🇷🇺 Русский', 'kz Қазақша'])
def select_language(message):
    if message.text == '🇺🇸 English':
        language = 'en'
    elif message.text == 'kz Қазақша':
        language = 'kz'
    else:
        language = 'ru'
    info['translations'] = load_translations(language)
    #print(info['translations'])
    #bot.register_next_step_handler(message, welcome)

def load_translations(language):
    if language == 'en':
        from lang_en import translations
    elif language == 'ru':
        from lang_ru import translations
    elif language == 'kz':
        from lang_kz import translations
    else:
        from lang_ru import translations
    return translations


@bot.message_handler(commands=['start'])
def main(message):
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    info['user_id'] = message.from_user.id
    info['user_name'] = message.from_user.username
    info['mention'] = f"@{info['user_name']}"
    memberInfo = bot.get_chat_member(chat_id, info['user_id'])
    if memberInfo.status == 'creator' or memberInfo.status == 'member':
        keyboard.add(*[telebot.types.KeyboardButton(text) for text in ['🇺🇸 English', '🇷🇺 Русский', 'kz Қазақша']])
        bot.send_message(message.chat.id, 'Выберите язык:', reply_markup=keyboard)
        bot.register_next_step_handler(message, select_language)
        bot.register_next_step_handler(message, load_translations)
        bot.register_next_step_handler(message, welcome)
    else:
        bot.send_message(message.chat.id, "Вы не подписаны на канал 'Tapsyrma' 😢! Пожалуйста, подпишитесь на канал, чтобы пользоваться нашим ботом. Ссылка на канал: t.me/tapsyrmachannel. \nПосле после этого вы можете снова запустить бота /start 👍.")




def welcome(message):
    bot.send_message(message.chat.id, text=info['translations']['welcome'])


@bot.message_handler(commands=['publication'])
def generate_public(message):
    bot.reply_to(message, info['translations']['gen_public'])
    bot.register_next_step_handler(message, generate_text)

def generate_text(message):
    info['text'] = message.text
    bot.reply_to(message, info['translations']['gen_text'])
    bot.register_next_step_handler(message, generate_price)

def generate_price(message):
    info['price'] = message.text
    try:
        if int(info['price']) > 0:
            bot.reply_to(message, info['translations']['gen_price_if'])
            bot.register_next_step_handler(message, generate_coment)
        else:
            bot.send_message(message.chat.id, info['translations']['gen_price_else'])
            bot.register_next_step_handler(message, generate_price)
    except:
        bot.send_message(message.chat.id, info['translations']['gen_price_else'])
        bot.register_next_step_handler(message, generate_price)

def generate_coment(message):
    info['coment'] = message.text
    bot.reply_to(message, info['translations']['gen_comment'])
    bot.register_next_step_handler(message, generate_pred)

@bot.message_handler(content_types=['photo'])
def generate_pred(message):
    if (info['text'] == '' or info['text'] == None) or (info['price'] == '' or info['price'] == None):
        bot.send_message(message.chat.id, info['translations']['gen_pred'])
    else:
        try:
            photo_id = str(message.photo[-1].file_id)
            info['photo_id'] = photo_id
            photo_info = bot.get_file(photo_id)
            photo_path = photo_info.file_path
        except:
            info['photo_id'] = '-'

        if info['photo_id'] != '-':
            caption = f"{info['translations']['tapsyrma']}: {info['text']}\n\n{info['translations']['bagasy']}: {info['price']}тг\n\n{info['translations']['coment']}: {info['coment']}\n\n{info['translations']['avtor']}: {info['mention']}"
            bot.send_photo(message.chat.id, info['photo_id'], caption)
        else:
            text = f"{info['translations']['tapsyrma']}: {info['text']}\n\n{info['translations']['bagasy']}: {info['price']}тг\n\n{info['translations']['coment']}: {info['coment']}\n\n{info['translations']['avtor']}: {info['mention']}"
            bot.send_message(message.chat.id, text=text)
        bot.send_message(message.chat.id, info['translations']['gen_pred_else'])
        
@bot.message_handler(commands=['listpublic'])
def generate_list_publications(message):
    cursor.execute('SELECT * FROM users WHERE user_id=?', (info['user_id'],))
    results = cursor.fetchall()
    #print(results)
    if results:
        text_link = info['translations']['list_public'] + "\n\n"
        count = 1
        for result in results:
            task_complete = info['translations']['nocomplete']
            id, user_id, username, message_id, complete = result
            if complete == 1:
                info['status'] = info['translations']['complete']
                task_complete = info['translations']['complete']
            message_list_link = f'https://t.me/{YOUR_CHANNEL_USERNAME}/{message_id}'
            text_link += str(count) + ". " + message_list_link + " (" + task_complete  + ")\n"
            count += 1
        bot.send_message(message.chat.id, text_link)
        bot.send_message(message.chat.id, info['translations']['complete_tasks'])
        bot.register_next_step_handler(message, complete_task)
    else:
        bot.send_message(message.chat.id, info['translations']['no_tasks'])
        
def complete_task(message):
    t = message.text
    try:
        complete_task_list = t.split(" ")
        cursor.execute('SELECT * FROM users WHERE user_id=?', (info['user_id'],))
        results = cursor.fetchall()
        if complete_task_list.count('0') >= 1:
            bot.send_message(message.chat.id, info['translations']['thanks_message'])
        else:
            if results:
                for i in complete_task_list:
                    id, user_id, username, message_id, complete = results[int(i)-1]
                    cursor.execute("UPDATE users SET complete=? WHERE message_id=?", (1, message_id))
                    conn.commit()
                    bot.send_message(message.chat.id, info['translations']['thanks_message'])
            else:
                bot.send_message(message.chat.id, info['translations']['no_tasks'])
    except:
        bot.send_message(message.chat.id, info['translations']['not_right'])
        bot.register_next_step_handler(message, complete_task)
        
            
    #print(t.split(" "))

@bot.message_handler(commands=['show'])
def show_public(message):
    #print(info)
    if info['photo_id'] != '-':
        caption = f"{info['translations']['tapsyrma']}: {info['text']}\n\n{info['translations']['bagasy']}: {info['price']}тг\n\n{info['translations']['coment']}: {info['coment']}\n\n{info['translations']['avtor']}: {info['mention']}"
        message_link = bot.send_photo(chat_id, info['photo_id'], caption)
    else:
        text = f"{info['translations']['tapsyrma']}: {info['text']}\n\n{info['translations']['bagasy']}: {info['price']}тг\n\n{info['translations']['coment']}: {info['coment']}\n\n{info['translations']['avtor']}: {info['mention']}"
        message_link = bot.send_message(chat_id, text=text)
    message_id = message_link.message_id
    db_table_val(id=message_link, user_id=info['user_id'], username=info['user_name'], message_id=str(message_id))
    messageLink = f'https://t.me/{YOUR_CHANNEL_USERNAME}/{message_id}'

    #print(f'Ссылка на сообщение: {messageLink}')

bot.polling()
