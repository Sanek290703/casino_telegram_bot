import telebot
from telebot import types
import time
import random

TOKEN = '8179628221:AAHD5uGen09w79wmhFZoDI1zKq2qYNrh_tM'
bot = telebot.TeleBot(TOKEN)

# Храним данные пользователей
user_data = {}  # user_id: {"balance": int, "state": str, "bet": int}

# --- Клавиатуры ---
def main_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(types.KeyboardButton("💰 Баланс"))
    kb.add(types.KeyboardButton("🏢 Идти работать"))
    kb.add(types.KeyboardButton("🎰 Казино"))
    return kb

def games_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(types.KeyboardButton("🪙 Орел или решка"))
    kb.add(types.KeyboardButton("✂️ Камень ножницы бумага"))
    kb.add(types.KeyboardButton("💵 Изменить ставку"))
    kb.add(types.KeyboardButton("🏠 Лобби"))
    return kb

def coin_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(types.KeyboardButton("Орел"))
    kb.add(types.KeyboardButton("Решка"))
    kb.add(types.KeyboardButton("🏠 Назад в лобби"))
    return kb

def rps_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(types.KeyboardButton("Камень"))
    kb.add(types.KeyboardButton("Ножницы"))
    kb.add(types.KeyboardButton("Бумага"))
    kb.add(types.KeyboardButton("🏠 Назад в лобби"))
    return kb

# --- Старт ---
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    user_data[user_id] = {"balance": 0, "state": "main", "bet": 10}  # ставка по умолчанию
    bot.send_message(message.chat.id,
                     "Привет, друг! 👋\nЯ твой игровой бот.\nВыбери действие:",
                     reply_markup=main_keyboard())

# --- Обработка главного меню ---
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    if user_id not in user_data:
        user_data[user_id] = {"balance": 0, "state": "main", "bet": 10}

    state = user_data[user_id]["state"]
    text = message.text

    # Проверяем состояние работы
    if state == "working":
        bot.send_message(message.chat.id, "⚠️ Ты сейчас на работе, подожди немного ⏳")
        return

    # Главные кнопки
    if text == "💰 Баланс":
        bot.send_message(message.chat.id, f"💵 Твой баланс: {user_data[user_id]['balance']}$\n💰 Текущая ставка: {user_data[user_id]['bet']}$")
        return

    elif text == "🏢 Идти работать":
        bot.send_message(message.chat.id, "Ты пошел работать... ⏳")
        user_data[user_id]["state"] = "working"
        time.sleep(3)  # имитация работы
        user_data[user_id]["balance"] += 20
        user_data[user_id]["state"] = "main"
        bot.send_message(message.chat.id, f"💼 Отличная работа! Ты заработал 20$\n💰 Баланс: {user_data[user_id]['balance']}$",
                         reply_markup=main_keyboard())
        return

    elif text == "🎰 Казино":
        bot.send_message(message.chat.id, "Добро пожаловать в казино! 🎲 Выбирай игру:", reply_markup=games_keyboard())
        user_data[user_id]["state"] = "casino"
        return

    # Казино
    if state == "casino":
        if text == "🪙 Орел или решка":
            bot.send_message(message.chat.id, f"💰 Текущая ставка: {user_data[user_id]['bet']}$\nВыбирай: Орел или Решка", reply_markup=coin_keyboard())
            bot.register_next_step_handler(message, coin_game)
            return

        elif text == "✂️ Камень ножницы бумага":
            bot.send_message(message.chat.id, f"💰 Текущая ставка: {user_data[user_id]['bet']}$\nВыбирай: Камень, Ножницы или Бумага", reply_markup=rps_keyboard())
            bot.register_next_step_handler(message, rps_game)
            return

        elif text == "💵 Изменить ставку":
            bot.send_message(message.chat.id, "Введите новую ставку (число):")
            bot.register_next_step_handler(message, change_bet)
            return

        elif text == "🏠 Лобби":
            bot.send_message(message.chat.id, "Возвращаемся в лобби 🏠", reply_markup=main_keyboard())
            user_data[user_id]["state"] = "main"
            return

        else:
            bot.send_message(message.chat.id, "⚠️ Выбери действие из меню", reply_markup=games_keyboard())
            return

# --- Изменение ставки ---
def change_bet(message):
    user_id = message.from_user.id
    try:
        new_bet = int(message.text)
        if new_bet <= 0:
            raise ValueError
        if new_bet > user_data[user_id]["balance"]:
            bot.send_message(message.chat.id, "⚠️ У тебя нет столько денег для этой ставки!")
            return
        user_data[user_id]["bet"] = new_bet
        bot.send_message(message.chat.id, f"💵 Ставка изменена на {new_bet}$", reply_markup=games_keyboard())
    except:
        bot.send_message(message.chat.id, "⚠️ Введи корректное число ставки!")
        bot.register_next_step_handler(message, change_bet)

# --- Орел/Решка ---
def coin_game(message):
    user_id = message.from_user.id
    choice = message.text.lower()

    if choice == "🏠 назад в лобби":
        bot.send_message(message.chat.id, "Возвращаемся в лобби 🏠", reply_markup=main_keyboard())
        user_data[user_id]["state"] = "main"
        return

    if choice not in ["орел", "решка"]:
        bot.send_message(message.chat.id, "⚠️ Неверный выбор! Выбери Орел или Решка")
        bot.register_next_step_handler(message, coin_game)
        return

    bet = user_data[user_id]["bet"]
    if bet > user_data[user_id]["balance"]:
        bot.send_message(message.chat.id, "⚠️ Недостаточно средств для ставки!")
        bot.register_next_step_handler(message, coin_game)
        return

    result = random.choice(["орел", "решка"])
    if choice == result:
        user_data[user_id]["balance"] += bet
        bot.send_message(message.chat.id, f"🪙 Выпало: {result.capitalize()}!\n🎉 Вы выиграли {bet}$\n💰 Баланс: {user_data[user_id]['balance']}$")
    else:
        user_data[user_id]["balance"] -= bet
        bot.send_message(message.chat.id, f"🪙 Выпало: {result.capitalize()}!\n😢 Вы проиграли {bet}$\n💰 Баланс: {user_data[user_id]['balance']}$")

    bot.send_message(message.chat.id, f"💰 Текущая ставка: {user_data[user_id]['bet']}$\nВыбирай: Орел или Решка", reply_markup=coin_keyboard())
    bot.register_next_step_handler(message, coin_game)

# --- Камень-ножницы-бумага ---
def rps_game(message):
    user_id = message.from_user.id
    choice = message.text.lower()

    if choice == "🏠 назад в лобби":
        bot.send_message(message.chat.id, "Возвращаемся в лобби 🏠", reply_markup=main_keyboard())
        user_data[user_id]["state"] = "main"
        return

    options = ["камень", "ножницы", "бумага"]
    if choice not in options:
        bot.send_message(message.chat.id, "⚠️ Неверный выбор! Выбери Камень, Ножницы или Бумага")
        bot.register_next_step_handler(message, rps_game)
        return

    bet = user_data[user_id]["bet"]
    if bet > user_data[user_id]["balance"]:
        bot.send_message(message.chat.id, "⚠️ Недостаточно средств для ставки!")
        bot.register_next_step_handler(message, rps_game)
        return

    bot_choice = random.choice(options)
    win_conditions = {"камень": "ножницы", "ножницы": "бумага", "бумага": "камень"}

    if choice == bot_choice:
        bot.send_message(message.chat.id, f"🤝 Бот выбрал {bot_choice.capitalize()}. Ничья!")
    elif win_conditions[choice] == bot_choice:
        user_data[user_id]["balance"] += bet
        bot.send_message(message.chat.id, f"🏆 Бот выбрал {bot_choice.capitalize()}.\n🎉 Вы выиграли {bet}$\n💰 Баланс: {user_data[user_id]['balance']}$")
    else:
        user_data[user_id]["balance"] -= bet
        bot.send_message(message.chat.id, f"😢 Бот выбрал {bot_choice.capitalize()}.\nВы проиграли {bet}$\n💰 Баланс: {user_data[user_id]['balance']}$")

    bot.send_message(message.chat.id, f"💰 Текущая ставка: {user_data[user_id]['bet']}$\nВыбирай: Камень, Ножницы или Бумага", reply_markup=rps_keyboard())
    bot.register_next_step_handler(message, rps_game)

# --- Запуск бота с авто-перезапуском ---
if __name__ == "__main__":
    while True:
        try:
            print("🚀 Бот запущен!")
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except Exception as e:
            print(f"⚠️ Ошибка: {e}. Перезапуск через 5 секунд...")
            time.sleep(5)
