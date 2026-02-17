import os
import sqlite3
import asyncio
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters, ConversationHandler
import aiohttp

admID = [2050385976]
API_oplat = "https://vdohnovi.bitrix24.ru/rest/601/c520oe9f4w80vppj/"
promo = 'ForYou'


async def start(update, text):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    knoopki = [[InlineKeyboardButton("Купить билеты", callback_data="1")],
               [InlineKeyboardButton("Сайт", callback_data="2", url="https://teachers2022.tilda.ws/page115956026.html")],
               [InlineKeyboardButton("ТГ-канал", callback_data="3",url="https://teachers2022.tilda.ws/page115956026.html")],
               [InlineKeyboardButton("Поддержка", callback_data="4")]]
    if user_id in admID:
        knoopki.append([InlineKeyboardButton("АДМИН-ПАНЕЛЬ", callback_data="adm")])

    marker = InlineKeyboardMarkup(knoopki)
    with open('11.jpg', 'rb') as photo:
        await text.bot.send_photo(chat_id=chat_id, photo=photo, caption="Привет\nинфа о фестивале", reply_markup=marker)

async def podderzka(update, text):
    qnop = update.callback_query
    await qnop.answer()
    if qnop.data == "4":
        await qnop.message.reply_text("Напишите ваще сообщение")

async def prodPodderzka(update, text):
    userID = update.effective_user.id
    textUS = update.message.text or ""
    if userID not in admID:
        await text.bot.send_message(
            chat_id=admID,
            text=f"ID:{userID}\nпомогите... \n\n{textUS}"        )
        await update.message.reply_text("Ваше сообщение отправлено")
        await start(update, text)
    elif update.message.reply_to_message:
        reply_to_text = update.message.reply_to_message.text or ""
        match = re.search(r"ID:(\d+)", reply_to_text)
        if match:
            target_id = int(match.group(1))
            await text.bot.send_message(
                chat_id=target_id,
                text=f"Ответ от поддержки:\n\n{textUS}"
            )
            await update.message.reply_text("Помощ в пути")

def bd():
    conn = sqlite3.connect("user.db")
    BD = conn.cursor()
    BD.execute('''
        CREATE TABLE IF NOT EXISTS user (
        ID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER UNIQUE,
        full_name TEXT,
        sdek_adress TEXT,
        FIO_ambasador TEXT,
        category_bilet TEXT,
        status TEXT DEFAULT 'moderation',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        moderated_at TIMESTAMP)
    ''')
    conn.commit()
    conn.close()

def regUS(tg_id, name, sdek, ambasador, category="all"):
    conn = sqlite3.connect("user.db")
    BD = conn.cursor()
    BD.execute('''
    INSERT OR REPLACE INTO user(telegram_id, full_name, sdek_adress, FIO_ambasador, category_bilet)
    VALUES(?,?,?,?,?)
    ''', (tg_id, name, sdek, ambasador, category))
    conn.commit()
    conn.close()
    print(f"Пользователь {name} зарегистрирован")
async def anketa(update, text):
    apdate = update.callback_query
    await apdate.answer()
    knoopki2 = [[InlineKeyboardButton("Продолжить", callback_data="prod")],
                [InlineKeyboardButton("Документы для обработки данных", callback_data="2",url="https://telegra.ph/Dokumenty-dlya-obrabotki-dannyh-02-13-2")],
                [InlineKeyboardButton("назад", callback_data="back")]]
    marker2 = InlineKeyboardMarkup(knoopki2)
    await apdate.message.reply_text(
        text="Для оформления билета на нужны следующие данны\n•тото\n•тата\n•тыты\nПродолжая беседу вы подтвержаете обраюотку ваших данных для бла бла",
        reply_markup=marker2)


fio, fiAmbasador, cdek, proverka = range(4)  # Убираем zavershenie, возвращаем как было
async def prodolzit(update, text):
    apdate = update.callback_query
    await apdate.answer()
    await text.bot.send_message(chat_id=update.effective_chat.id, text="✍️ Введите ваше ФИО:")
    return fio

async def fiAmbasador1(update, text):
    text.user_data["fio"] = update.message.text
    await text.bot.send_message(chat_id=update.effective_chat.id, text="🌟Укажите ваш контактный номер")
    return fiAmbasador

async def cdek1(update, text):
    text.user_data["fiAmbasador"] = update.message.text
    await text.bot.send_message(chat_id=update.effective_chat.id, text="🤑Ваша должность:")
    return cdek

async def podarok1(update, text):
    text.user_data["dolznost"] = update.message.text
    await text.bot.send_message(
        chat_id=update.effective_chat.id,
        text="🎁 Есть промокод?\nЕсли у вас есть секретный ключ к скидке - введите его ниже!\nИли просто отправьте '-' чтобы продолжить:"
    )
    return proverka


async def proverkaProm(update, context):
    promocode = update.message.text.strip()

    if promocode.lower() == promo.lower():
        await update.message.reply_text("🎉 Промокод принят!")
        context.user_data["promo"] = promo
        return await conets(update, context)

    elif promocode == "-":
        await update.message.reply_text("Продолжаем без промокода.")
        context.user_data["promo"] = "all"
        return await conets(update, context)

    else:
        await update.message.reply_text("❌ Неверный промокод.\nПопробуйте ещё или отправьте '-'")
        return proverka

async def conets(update, text):
    tg_id = update.effective_chat.id
    full_name = text.user_data.get("fio", "")
    sdek = text.user_data.get("dolznost", "")
    FIO_ambasador = text.user_data.get("fiAmbasador", "")
    category = text.user_data.get("promo", "all")
    regUS(tg_id, full_name, sdek, FIO_ambasador, category)
    await daNET(update, text, tg_id, full_name, FIO_ambasador, sdek)
    await update.message.reply_text("✅ Анкета отправлена на проверку, мы сообщим о результате")
    return ConversationHandler.END

obrab = ConversationHandler(
    entry_points=[CallbackQueryHandler(prodolzit, pattern="^prod$")],
    states={
        fio: [MessageHandler(filters.TEXT & ~filters.COMMAND, fiAmbasador1)],
        fiAmbasador: [MessageHandler(filters.TEXT & ~filters.COMMAND, cdek1)],
        cdek: [MessageHandler(filters.TEXT & ~filters.COMMAND, podarok1)],
        proverka: [MessageHandler(filters.TEXT & ~filters.COMMAND, proverkaProm)],
    },
    fallbacks=[],
)


async def oplacheniePolzovat(update, text):
    chat_id = update.effective_chat.id
    knoopki11 = [[InlineKeyboardButton("ТОП 10 ПАЛАТОК", callback_data="1")],[InlineKeyboardButton("Связаться с нами", callback_data="2")],[InlineKeyboardButton("ТГ-канал", callback_data="3")]]
    marker = InlineKeyboardMarkup(knoopki11)
    await update.message.reply_text(chat_id=chat_id, caption="Привет\nинфа число для платочных юзеров",reply_markup=marker)


categor, sms = range(2)
categoriaRassilki = {
    "all": "📢 Всем пользователям",
    "tolkoBye": "Только купившие билеты",
    "VIP": "👑 VIP ",
    "withPokishat": "Билеты с питонием"}


async def admin(update, context):
    if update.callback_query:
        z = update.callback_query
        await z.answer()
        user_id = z.from_user.id
        message = z.message
        reply_method = message.reply_text
    else:
        user_id = update.effective_user.id
        message = update.message
        reply_method = message.reply_text
    knop = [[InlineKeyboardButton("Рассылка", callback_data="adm_M")],[InlineKeyboardButton("Статистика", callback_data="stat")],[InlineKeyboardButton("Назад", callback_data="adm_exit")]]
    reply_markup = InlineKeyboardMarkup(knop)
    await reply_method("АДМИН-ПАНЕЛЬ\nВыберите действие", reply_markup=reply_markup)


async def otpSms(update, context):
    qq = update.callback_query
    await qq.answer()
    user_id = qq.from_user.id
    if qq.data == "adm_M":
        knop = []
        for categories_id, category_name in categoriaRassilki.items():
            knop.append([InlineKeyboardButton(category_name, callback_data=f"mailing_{categories_id}")])
        knop.append([InlineKeyboardButton("Назад", callback_data="adm_exit")])
        reply_markup = InlineKeyboardMarkup(knop)
        await qq.edit_message_text("Выберете категорию для рассылки", reply_markup=reply_markup)
        return
    elif qq.data.startswith('mailing_'):
        category = qq.data.replace('mailing_', '')
        context.user_data['rasilka'] = category
        await qq.edit_message_text(f"Выбрана категория: {categoriaRassilki.get(category, category)}\nВведите сообщение:")
        return


async def get_massage(update, context):
    text = update.message.text
    category = context.user_data.get('rasilka', 'all')
    conn = sqlite3.connect("user.db")
    BD = conn.cursor()
    if category == "all":
        BD.execute("SELECT telegram_id,full_name FROM user")
        category_name = 'всем'
    elif category == "VIP":
        BD.execute("SELECT telegram_id,full_name FROM user WHERE category_bilet = 'VIP'")
        category_name = 'vip'
    elif category == "withPokishat":
        BD.execute("SELECT telegram_id,full_name FROM user WHERE category_bilet = 'withPokishat'")
        category_name = 'С поесть'
    elif category == "tolkoBye":
        BD.execute("SELECT telegram_id,full_name FROM user WHERE category_bilet != 'all'")
        category_name = 'только купили'
    else:
        BD.execute("SELECT telegram_id, full_name FROM user")
        category_name = "всем пользователям"
    users = BD.fetchall()
    conn.close()
    us = len(users)
    allUSER = len(users)
    status = await update.message.reply_text(f"Отправлено {allUSER}")
    f = 0
    for user_data in users:
        user_id = user_data[0]
        await context.bot.send_message(chat_id=user_id, text=text)
        f += 1
        await asyncio.sleep(0.05)
        await admin(update, context)
    return ConversationHandler.END

async def adm_exit(update, context):
    qq = update.callback_query
    await qq.answer()
async def bitrix(user_data, chsena = 2134):
    url = API_oplat + "crm.deal.add"
    contact = await seeContact(user_data)
    sdelka = {
        "fields":{
            "nazvaniie": f"покупка билета - {user_data.get('fio', '')}",
            "stadia": "new",
            "valuta": "rub",
            "сumma": chsena,
            "ID": contact,
            "CRM_TG": user_data.get('tg_id', ''),
            "coment": f"Адрес СДЭК: {user_data.get('sdek_adress', '')}\nАмбасадор: {user_data.get('fiAmbasador', '')}"
        }
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=sdelka) as resp:
            return await resp.json()
async def seeContact(user_data):
    url = API_oplat + "crm.contact.list"
    filter = {"filter": {"CRM_TG": user_data.get('tg_id', '')}}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=filter) as resp:
            resp_json = await resp.json()
            if resp_json.get('result'):
                return resp_json['result'][0]['ID']
    url = API_oplat + "crm.contact.add"
    fio_all = user_data.get('fio', '').split()
    firsName = fio_all[0] if fio_all else 'участник'
    lastName = ' '.join(fio_all[1:] if len(fio_all) > 1 else '')

    dannie = {
        "fields":{
            'name': firsName,
            'lastName': lastName,
            'CRm_TG': user_data.get('tg_id', ''),

        }
    }
    async with aiohttp.ClientSession() as session2:
        async with session2.post(url, json=dannie) as resp:
            result = await resp.json()
            return result.get('result')

async def proverka(update, text):
    query = update.callback_query
    oplacheno = await proverka(API_oplat)
    if oplacheno == "PAID":
        await query.answer("Оплата подтверждена!")
        await query.edit_message_text(text="Оплата прошла",reply_markup=oplacheniePolzovat)

def saveID(user_id, user_data):
    conn = sqlite3.connect('bot_base.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO ankety (user_id, fio, phone, position) VALUES (?, ?, ?, ?)",(user_id, user_data['fio'], user_data['fiAmbasador'], user_data['dolznost']))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return new_id

async def daNET(update, context, tg_id, full_name, phone, position):
    rand_id = str(tg_id)
    key = [[InlineKeyboardButton("✅ ДА", callback_data=f"moder_yes_{tg_id}"),InlineKeyboardButton("❌ НЕТ", callback_data=f"moder_no_{tg_id}")]]
    await context.bot.send_message(chat_id=admID,text=f"Новая анкета\nот {context.user_data['fio']}\nf""Должность: {context.user_data['dolznost']}",reply_markup=InlineKeyboardMarkup(key),parse_mode="Markdown")
    for adminID in admID:
        await context.bot.send_message(chat_id = adminID,text=f'Анкета:\nФИО:{full_name}\nТелефон:{phone}\nдолжность:{position}\nid:{tg_id}', reply_markup=InlineKeyboardMarkup(key))

async def obrDaNet(update,text):
    query = update.callback_query
    await query.answer()
    data = query.data
    action = data.split('_')[1]
    userTG_id = int(data.split('_')[2])
    if action == 'yes':
        update_user_statys(userTG_id, 'confirmed')
        await query.edit_message_text('✅ Анкета подтверждена')
        await text.bot.send_message(chat_id = userTG_id,text='✅ Анкета подтверждена, теперь вы можите оплатичвать билет')
        key = [InlineKeyboardButton('Перейти к оплате', callback_data=f"pay{userTG_id}")]
        await text.bot.send_message(chat_id=userTG_id,text='Для оплаты билета нажмите кнопку ниже:',reply_markup=InlineKeyboardMarkup(key))
    elif action == 'no':
        update_user_statys(userTG_id, 'rejected')
        await query.edit_message_text(chat_id=userTG_id,text="❌ К сожалению, ваша анкета не прошла модерацию. Свяжитесь с поддержкой для уточнения инфорации.")

def update_user_statys(tg_id, status):
    conn = sqlite3.connect('bot_base.db')
    BD = conn.cursor()
    BD.execute('''UPDATE user SET status=?, modereted_at=CURRENT_TIMSTAMP WHERE telegram_id=? ''', (status, tg_id))
    conn.commit()
    conn.close()
    print(f'статус юзера {tg_id} изменен на {status}')

def main():
    bd()
    BOT_TOKEN = os.environ.get('BOT_TOKEN', '8329705097:AAHYdfm3Ce815BMkcGhFz-CSk6nMGz7wZX8')
    ADMIN_ID = int(os.environ.get('ADMIN_ID', '2050385976'))
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(obrab)
    app.add_handler(CallbackQueryHandler(anketa, pattern="^1$"))
    app.add_handler(CallbackQueryHandler(podderzka, pattern="^4$"))
    app.add_handler(CallbackQueryHandler(admin, pattern="^adm$"))
    app.add_handler(CallbackQueryHandler(start, pattern="^back$"))
    app.add_handler(CallbackQueryHandler(start, pattern="^adm_exit$"))
    app.add_handler(CallbackQueryHandler(obrDaNet, pattern="^moder_"))
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(otpSms, pattern='^adm_M$')],
        states={categor: [CallbackQueryHandler(otpSms, pattern='^mailing_')],sms: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_massage)]},
        fallbacks=[CallbackQueryHandler(adm_exit, pattern='^adm_exit$')],
        per_message=False,
    )
    app.add_handler(conv_handler)
    app.add_handler(MessageHandler(filters.Regex('^/admin$'), admin))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, prodPodderzka))
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
