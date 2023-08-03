import logging
import os
from datetime import timedelta, datetime

import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import InputFile, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.utils import executor
import asyncio

from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.middlewares.logging import LoggingMiddleware

API_TOKEN = '6374996873:AAHC8QoTa9Bfwme-CMaRB0rADZuuWevADxw'

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
# logging.basicConfig(level=logging.INFO)

# Словарь с вопросами и соответствующими callback_data
questions_dict = {
    'registration_roboforex': 'Регистрация на брокере "ROBOFOREX"',
    'registration_binance': 'Регистрация на криптовалютной бирже "Binance"',
    'replenishment_broker_account': "Пополнение брокерского счета",
    'withdrawal_broker_account': "Вывод средств с брокерского счета",
    'remote_desktop_registration': "Регистрация удаленного рабочего стола (УРС)",
    'order_rd_installation': "Заказ УРС для двух терминалов и их установка",
    'terminal_installation_rd': "Установка торгового терминала на УРС и подключение торгового счета",
    'opening_partner_account': "Открытие партнерского счета",
    'eve_installation_setup': "Установка и настройка EVE",
    'hermes_installation_setup': "Установка и настройка HERMES",
    'forex_for_beginners': "FOREX для начинающих"
}

faq_dict = {
    "question1": ["Торговый советник ( робот ) – это ?!",
                  "Торговый советник ( робот ) – это математический алгоритм, взаимодействие уникальной иновационной системы индикаторов с искусственным интеллектом.\nПринцип работы устроен таким образом, чтобы вы могли зарабатывать на валютных биржах, не имея практической / технической базы в сфере инвестирования.\n\nНезависимо от ГЕО.\nНаблюдая за процессом с моб. устройства."],
    "question2": ["Кому подойдет торговый советник ?!",
                  "ВСЕМ.\n\nТорговые советник подойдет – инвесторам для увеличения капитала, сотрудникам найма для накопления уже заработанных средств.\n\nИнвесторы, средний | малый бизнес, сотрудники найма, фрилансеры и тд.\nСколько бы вы не зарабатывали 20%+ к этой цифре в месяц - всегда приятно.\n\nденьги – делают деньги.\n\nПри помощи торговых советников, вы можете увеличивать прибыль от 20% в месяц, а с учетом рекапитализации и сложного процента это более 350% годовых."],
    "question3": ["Отличия торгового советника EVE от HERME$",
                  "EVE — это агрессивный торговый советник, который подойдёт для тех, кто в кратчайшие сроки хочет увеличить свой депозит.\n\nПоказателем надёжности стратегии, можно считать пройденные, самые волатильные\nи опасные участки на истории графика.\n\nВ среднем советник закрывает 800+ сделок в месяц, 75% из которых - прибыльные.\n\nБлагодаря трейлинг-стопу, сделки закрываются в профит более 15% к депозиту за один раз!\n\nПрибыль начинается от 20% в месяц на консервативных настройках.\n\nВ Декабре 2022г, робот сделал +77,5% за 4 торговых дня благодаря трейлинг-стопу.\n\n\nHERME$ — это надежный торговый советник, который подойдёт для тех, кто по большей степени хочет получать 6-8% в месяц, при этом максимально комфортно чувствовать себя в критические ситуации на рынке.\n\nАлгоритм данного торгового советника основан на методе сеточной торговли.\n\nИндикатор Relative Strength Index - определяет тренд движения, после чего поступает сигнал на вход или игнорирование входа в рынок.\nЕсли после открытия позиции, цена идёт в сторону открытой сделки BUY или SELL, то советник дожидается условий для фиксации прибыли и закрывает сделку.\nHERME$ способен фиксировать прибыль как по тейк-профиту, так и при помощи сопровождения трейлинг-стопа, что позволит получать максимальный профит на откатах рынка в нужную сторону.\nЕсли график идёт в противоположную сторону, советник анализирует рынок для усреднения средней цены входа и улучшения условий для закрытия всех текущих позиций.\nВ случае затяжных трендовых движений, HERME$ будет минимизировать риски изменения цены путём открытия позиций в противоположную сторону, начиная страховать ваши позиции с 3-го и по 8-ой ордер включительно, далее хеджирование прекратиться.\n\nЯ, лично использую EVE & HERME$.\nТ.к. это разные торговые советники, разный принцип работы, эти роботы друг друга компенсируют, один зарабатывает, на повышенной волатильности, другой, когда рынок более спокойный.\n\nВ моей команде, люди используют реинвестирование прибыли с EVE на HERMES.\nВы зарабатываете с вашего основного депозита + 6-8 % с заработанных средств."],
    "question4": ["Депозит | пополнение | вывод средств",
                  "Депозит.\nНаходиться на вашем брокерском счете.\nБрокер - RoboForex, является одним из лидеров на рынке. Основан в 2009 году.\nВаши средства не находятся в доверительном управлении.\nРазличные вмешательства 3 лиц исключены.\n\nПополнение.\nЕсть различные варианты пополнения брокерского счета, в основном пополнение происходит через USDT, тк это самый выгодный метод. Но, так же вы можете пополнять через вашу банковскую карту. Либо, выбрать из предоставленных брокером – удобный для вас способ пополнения.\n\nВывод средств.\nПроисходит аналогичным способом как и пополнение, заявки в основном обрабатываются в пределах 5-10 минут в рабочее время, условиями брокера вывод может занимать до 2х рабочих дней.\n\nЕсть комиссия и конвертация валют\n≈ 1% на ввод / вывод средств.\n2 раза в месяц, брокер предоставляет возможность на вывод средств без комиссии."],
    "question5": ["Где | как и на чём происходит торговля ?!",
                  "Торговля происходит на рынке Forex.\nНа протяжении 5 лет мы используем проверенного брокера RoboForex.\nОснован в 2009 году.\nЯвляется одним из лидирующих брокеров, стабильно занимает различные номинации и награды среди лучших брокеров мира.\nНикаких спорных ситуаций, касаемо вывода средств, торговли в целом не наблюдалось.\nПоддержка всегда идет на встречу и готова ответить на все ваши вопросы, за каждым клиентом закрепляется личный менеджер.\n\nТорговля происходит в паре XAU | USD\nЗолото | доллар.\nМы не закупаем актив с мыслями о том, что он подорожает в цене и мы заработаем. Мы зарабатываем, и когда цена на золото растет, и когда цена на золото падает.\nДоход происходит в долларах ($)."],
    "question6": ["Почему именно МЫ, а не конкуренты ?!",
                  "У нас есть лицо, лояльность в глазах порядка 3000 человек.\nПродано более 7000 торговых советников.\nНам доверяют и с нами зарабатывают.\n\nКасаемо цены, качественный продукт – не может быть дешевым. Нет цели продать как можно больше, есть внутренняя политика, и в ней в первую очередь заложены такие понятия, как честность, открытость и доверие.\n\nМы успешно прошли самые важные экономические события на финансовом рынке за последние 10 лет, такие как Covid-19, спецоперации, выборы и прочие не мало важные заявления, отчеты, выступления.\n\nКасаемо доходности, цифры - лучшие показатели и факты.\nВся статистика максимально открыта и зеркальна. Ничего не придумывая, не скрашивая различные ситуации, как есть.\nМожно обратиться и получить статистику за выбранный период."],
    "question7": ["Покупая торгового советника, вы получаете",
                  "Покупая торгового советника, вы получаете индивидуальный личный файл, который принадлежит строго только вам, и работать он будет только на вашем брокерском счете.\nРазличные вмешательства 3-х лиц исключены.\nТакже, вы будете добавлены в чат единомышленников, где есть различные комнаты: для общения | вопросов | новостей | результатов и прочих моментов.\n\nЕсть PDF-инструкции со всеми разъяснениями, есть служба поддержки | коллектив, который всегда придет к вам на помощь, словом | делом от А до Я."],
    "question8": ["Отличия торгового советника, от трейдинга (торговли руками)",
                  "Робот - это автоматизированный процесс.\n\nОТЛИЧИЯ ОТ КЛАССИЧЕСКОГО ТРЕЙДЕРА.\n\n1. Становитесь свободным от аналитики.\n(Изучения новостей, построения графиков и прочих тонкостей финансовых рынков)\n\n2. Отсутствие человеческого фактора.\n(Сон, еда и прочие потребности)\n\n3. Многозадачность.\n(Робот анализирует, открывает и закрывает сделки, за считанные секунды, что физически реализовать человеку - невозможно)"],
    "question9": ["Почему именно золото | доллар XAU | USD, а не другие валюты ?!",
                  "Золото - защитный актив, было, есть и будет на рынке торговли.\n\nЗолото менее волатильно по сравнению с другими валютами. В нынешнее время, в какой-то стране стоит чихнуть или сказать что-то, и уже цена валюты полетела.\n\nЗолото конечно имеет характер, но как правило, это обоснованно и предсказуемо."],
    "question10": ["Доходность | с какой суммы можно начать ?!",
                   "Доходность зависит от выбранного вами торгового советника.\nДоходность в долларах ($).\n\nEVE - цена торгового советника 74.990 ₽.\nДоходность от 25% в месяц.\nРекомендуемый депозит от 500$.\n\nHERME$ - цена торгового советника 34.990 ₽.\nДоходность 6-8% в месяц.\nРекомендуемый депозит 200$."],
    "question11": ["Нужны ли знания|обучения|образование ?!",
                   "Нет. Нужно - желание.\nВажно, чтобы ваш возраст был 18+\n\nОстальное мы берём на себя, буквально 3-4 недели и вы поймете, что в какой-то степени даже обычный онлайн банк на телефоне, гораздо сложнее.\n\nНе волнуйтесь. У вас все получится."],
    "question12": ["Что входит помимо торгового советника ?!",
                   "• Полную инструкцию и сопровождение по настройке и установке торгового советника.\n• Обучение по работе с программным обеспечением.\n• Доступ в чат единомышленников."],
    "question13": ["Кредиты | займы | последние деньги",
                   "Такое – Не приветствуется.\n\nВы должны понимать, что это рынок.\nЕсть ли риски, конечно есть.\nАналогично, когда вы храните деньги под подушкой или относите средства в банк.\n\nВся банковская система и есть риск.\nДефолт, банкротство банка - денег нет.\n\nНо, сами знаете, самый большой риск - так и не рискнуть.\n\nМои рекомендации: не спишите к большим деньгам | депозитам | доходам.\n\nВ первую очередь разберитесь в алгоритме, как это работает.\n\nПоверьте, как только будет насмотренность и понимание, у вас не возникнет вопросов | сомнений касаемо работоспособности этого инструмента."],
    "question14": ["Рекомендуемые настройки",
                   "На протяжении всего времени мы тестируем, дорабатываем и обновляем, как сам алгоритм, так и рекомендации по работе с каждым торговым советником.\n\nЭти цифры - ориентир в максимально волатильные дни на финансовых рынках.\n\nВ первую очередь мы обязаны сохранить средства, а уже после приумножить.\n\nПридерживайтесь рекомендаций и все у вас будет хорошо."]
}

# Загрузка списка картинок
images_list = ['images/1.jpg', 'images/2.jpg', 'images/3.jpg', 'images/4.jpg', 'images/5.jpg', 'images/6.jpg']


# Функция для создания инлайн кнопки "Далее"
def get_inline_keyboard():
    inline_keyboard = InlineKeyboardMarkup()
    inline_keyboard.add(InlineKeyboardButton("Далее", callback_data="next"))
    return inline_keyboard


# Функция для отправки следующей картинки
async def send_next_image(message: types.Message):
    if not hasattr(send_next_image, "current_image_index"):
        send_next_image.current_image_index = 0

    current_image_index = send_next_image.current_image_index

    if current_image_index < len(images_list):
        image_path = images_list[current_image_index]
        with open(image_path, 'rb') as photo:
            await message.answer_photo(photo, reply_markup=get_inline_keyboard())

        send_next_image.current_image_index += 1
    else:
        await show_main_menu(message)


# Функция для показа главного меню
async def show_main_menu(message: types.Message):
    keyboard_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons_row1 = ["Торговые советники"]
    buttons_row2 = ["Расчет профита", "Новости недели"]
    buttons_row3 = ["Необходимые сервисы", "FAQ"]
    keyboard_markup.add(*buttons_row1)
    keyboard_markup.row(*buttons_row2)
    keyboard_markup.row(*buttons_row3)
    await message.answer("Привет! Что вас интересует?", reply_markup=keyboard_markup)


# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    send_next_image.current_image_index = 0
    await send_next_image(message)


# Обработчик нажатия на инлайн кнопку "Далее"
@dp.callback_query_handler(lambda c: c.data == 'next')
async def process_callback_next(callback_query: CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await send_next_image(callback_query.message)


async def fetch_calendar_events(start_date, end_date):
    try:
        url = "https://news.investforum.ru/events/?f=json&culture=ru&view=range&start={0}&end={1}&countrycode=AR,AU," \
              "AT,BE,BR,CA,CL,CN,CO,CZ,DK,EMU,DE,FI,FR,GR,HK,HU,IS,IN,ID,IE,IT,JP,MX,NL,NZ,NO,PL,PT,RO,RU,SG,SK,ZA," \
              "KR,ES,SE,CH,TR,UK,US,PE&categories=c94405b5-5f85-4397-ab11-002a481c4b92," \
              "33303f5e-1e3c-4016-ab2d-ac87e98f57ca,e229c890-80fc-40f3-b6f4-b658f3a02635," \
              "91da97bd-d94a-4ce8-a02b-b96ee2944e4c,24127f3b-edce-4dc4-afdf-0b3bd8a964be," \
              "fa6570f6-e494-4563-a363-00d0f2abec37,e9e957ec-2927-4a77-ae0c-f5e4b5807c16," \
              "7dfaef86-c3fe-4e76-9421-8958cc2f9a0d," \
              "9c4a731a-d993-4d55-89f3-dc707cc1d596&volatility=3&timezone=Russian+Standard+Time".format(
            start_date.strftime("%Y%m%d"), end_date.strftime("%Y%m%d"))
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json(content_type="text/plain")
                else:
                    return None
    except (aiohttp.ClientOSError, asyncio.TimeoutError):
        return None


def format_calendar_message(events):
    msg = "<b>Экономический календарь на текущую неделю</b>\nЧасовой пояс МСК\n\n"
    if events:
        date_time_obj_date = ''
        for event in events:
            date_time_str = event['DateTime']['DateStr']
            date_time_obj = datetime.strptime(date_time_str, '%Y%m%d %H:%M:%S')
            if date_time_obj.date() != date_time_obj_date:
                date_time_obj_date = date_time_obj.date()
                msg += f"📅 <b>{date_time_obj.date()}</b>\n\n"
            msg += "<b>{time} {country} {currency}</b>\n{name}\n".format(
                time=date_time_obj.time().strftime('%H:%M'),
                country=event['Country'],
                currency=event['Currency'],
                name=event['Name']
            )
            if event['DisplayActual'] or event['DisplayConsensus'] or event['DisplayPrevious']:
                msg += "{actual}{consensus}{previous}\n".format(
                    actual='<b>Факт.:</b> <code>{}</code> '.format(event['DisplayActual']) if event[
                        'DisplayActual'] else '',
                    consensus='<b>Прогноз:</b> <code>{}</code> '.format(event['DisplayConsensus']) if event[
                        'DisplayConsensus'] else '',
                    previous='<b>Пред.:</b> <code>{}</code> '.format(event['DisplayPrevious']) if event[
                        'DisplayPrevious'] else ''
                )
            msg += "\n"
    return msg


async def send_robot_options(message: types.Message):
    keyboard_markup = types.InlineKeyboardMarkup(row_width=2)
    hermes_button = types.InlineKeyboardButton("HERMES", callback_data="hermes")
    eve_button = types.InlineKeyboardButton("EVE", callback_data="eve")
    keyboard_markup.add(hermes_button, eve_button)

    await message.reply("Выберите торгового помошника:", reply_markup=keyboard_markup)


@dp.callback_query_handler(lambda query: query.data in ["hermes", "eve"])
async def process_robot_selection(query: types.CallbackQuery):
    robot = query.data
    if robot == "hermes":
        caption = "Профессиональный инструмент , который подходит как для новичков, так и для опытных трейдеров. HERME$ оценивает текущее состояние рынка, снижает возможные риски и увеличивает прибыль.\nТорговля предусмотрена на валютной паре: XAUUSD (Золото/Доллар)\nСтоимость: 34.990 рублей"
        photo_file = "images/hermes.jpg"
    elif robot == "eve":
        caption = "EVE - это советник, имеющий современный и агрессивный торговый алгоритм, подходящий для опытных трейдеров.\nТорговля предусмотрена на валютной паре: XAUUSD (Золото/Доллар).\nПоказателем надёжности стратегии, можно считать прохождение самых волатильных и опасных участков графика биржевого рынка.\nСтоимость: 74.990 рублей"
        photo_file = 'images/eve.jpg'
    else:
        return

    with open(photo_file, 'rb') as photo:
        await bot.send_photo(chat_id=query.from_user.id, photo=photo, caption=caption,
                             reply_markup=types.InlineKeyboardMarkup().add(
                                 types.InlineKeyboardButton("Приобрести торгового советника",
                                                            callback_data="bya_robot")))


# Обработка нажатия на кнопку "Bya Robot"
@dp.callback_query_handler(lambda query: query.data == "bya_robot")
async def process_bya_robot(query: types.CallbackQuery):
    await query.answer()  # Отправляем пустой ответ, чтобы убрать "часики" у пользователя

    # Добавляем инлайн кнопку для открытия FAQ
    inline_keyboard_markup = types.InlineKeyboardMarkup()
    inline_keyboard_markup.add(types.InlineKeyboardButton("FAQ", callback_data="faq"))
    await bot.send_message(query.from_user.id, "Внимание! Обязательно прочтите FAQ\n\n"
                                               "Для приобретения торгового советника свяжитесь с @pipisods",
                           reply_markup=inline_keyboard_markup)


class ProfitCalculationState(StatesGroup):
    waiting_for_amount = State()
    waiting_for_lot = State()


async def ask_for_amount(message: types.Message):
    # Создаем клавиатуру с кнопкой "Закончить расчет профита"
    keyboard_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard_markup.add(types.KeyboardButton("Закончить расчет профита"))

    await message.reply("Введите сумму для расчета:", reply_markup=keyboard_markup)
    await ProfitCalculationState.waiting_for_amount.set()


@dp.message_handler(state=ProfitCalculationState.waiting_for_amount)
async def process_amount(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        sum_for_calculation = message.text
        await state.update_data(sum_for_calculation=sum_for_calculation)

        keyboard_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard_markup.add("0.01", "0.015", "0.02")
        keyboard_markup.add("Закончить расчет профита")

        await message.reply("Выберите лот:", reply_markup=keyboard_markup)
        await ProfitCalculationState.waiting_for_lot.set()
    else:
        await finish_profit_calculation(message, state)
        return


@dp.message_handler(state=ProfitCalculationState.waiting_for_lot)
async def process_profit_calculation(message: types.Message, state: FSMContext):
    if message.text in ["0.01", "0.015", "0.02"]:
        data = await state.get_data()
        sum_for_calculation = data.get("sum_for_calculation")

        orders = {
            "0.01": [0.18, 0.3, 0.5, 0.83, 1.32, 2.175, 3.59, 5.925, 9.78, 16.14, 26.635],
            "0.015": [0.27, 0.45, 0.75, 1.245, 1.98, 3.265, 5.385, 8.8875, 14.67, 24.21, 39.9525],
            "0.02": [0.36, 0.6, 1, 1.66, 2.64, 4.35, 7.18, 11.85, 19.56, 32.28, 53.27],
        }

        result_message = "Напоминаю, лот завышать нельзя! Работаем не больше 0.02/1000 баксов, имея при таком лоте 100% долив. Прибыль указана приблизительно, так как существуют еще комиссии и очередность исполнения ордеров по достижению take-profit цены\n\n"
        for i, order in enumerate(orders[message.text], 10):
            profit = float(sum_for_calculation) / 100 * order
            result_message += f"{i}ый ордер {profit:.2f}$ | {order:.2f}%\n"

        await bot.send_message(chat_id=message.from_user.id, text=result_message)
    else:
        await finish_profit_calculation(message, state)
        return


@dp.message_handler(lambda message: message.text == "Закончить расчет профита")
async def finish_profit_calculation(message: types.Message, state: FSMContext):
    # Сброс состояния
    await state.finish()

    # Создаем новую клавиатуру с вашими кнопками
    keyboard_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons_row1 = ["Торговые советники"]
    buttons_row2 = ["Расчет профита", "Новости недели"]
    buttons_row3 = ["Необходимые сервисы", "FAQ"]
    keyboard_markup.add(*buttons_row1)
    keyboard_markup.row(*buttons_row2)
    keyboard_markup.row(*buttons_row3)

    await message.answer("Расчет профита завершен.", reply_markup=keyboard_markup)


# Функция для отправки пользователю PDF-файла
async def send_pdf(chat_id, question):
    pdf_file_path = os.path.join('pdf', f'{question}.pdf')
    with open(pdf_file_path, 'rb') as file:
        await bot.send_document(chat_id, file)


# Функция для отправки пользователю URL-ссылки
async def send_url(chat_id, url):
    await bot.send_message(chat_id, f"Откройте ссылку: {url}")


# Обработка нажатия на конкретный вопрос
@dp.callback_query_handler(lambda query: query.data in questions_dict.keys())
async def process_question_callback(callback_query: types.CallbackQuery):
    await callback_query.answer()  # Отправляем пустой ответ, чтобы убрать "часики" у пользователя
    question = callback_query.data  # questions_dict[callback_query.data]
    await send_pdf(callback_query.from_user.id, question)


@dp.callback_query_handler(lambda query: query.data == "faq_questions")
async def open_faq_questions(callback_query: types.CallbackQuery):
    await callback_query.answer()  # Отправляем пустой ответ, чтобы убрать "часики" у пользователя
    inline_keyboard_markup = types.InlineKeyboardMarkup(row_width=1)
    for key, value in faq_dict.items():
        question = value[0]
        inline_keyboard_markup.add(types.InlineKeyboardButton(text=question, callback_data=key))
    await bot.send_message(callback_query.from_user.id, "Часто задаваемые вопросы:",
                           reply_markup=inline_keyboard_markup)


@dp.callback_query_handler(lambda query: query.data in faq_dict.keys())
async def send_faq_answer(callback_query: types.CallbackQuery):
    question_key = callback_query.data
    question, answer = faq_dict.get(question_key)
    await callback_query.message.answer(f"{question}\n\n{answer}")


# Создаем новый обработчик для "Установка торгового помощника"
@dp.callback_query_handler(lambda query: query.data == "faq_assistant")
async def open_faq_assistant(callback_query: types.CallbackQuery):
    await callback_query.answer()  # Отправляем пустой ответ, чтобы убрать "часики" у пользователя
    inline_keyboard_markup = types.InlineKeyboardMarkup(row_width=1)

    # Добавляем вопросы из "Часто задаваемые вопросы" в раздел "Установка торгового помощника"
    for callback_data, question in questions_dict.items():
        inline_keyboard_markup.add(types.InlineKeyboardButton(question, callback_data=f"faq_answer_{callback_data}"))
    await bot.send_message(callback_query.from_user.id, "Установка торгового помощника:",
                           reply_markup=inline_keyboard_markup)


# Обработчик для вопросов и ответов в разделе "Установка торгового помощника"
@dp.callback_query_handler(lambda query: query.data.startswith("faq_answer_"))
async def process_faq_assistant_answer_callback(callback_query: types.CallbackQuery):
    await callback_query.answer()  # Отправляем пустой ответ, чтобы убрать "часики" у пользователя
    question_key = callback_query.data[len("faq_answer_"):]  # Получаем ключ вопроса из callback_data
    question = questions_dict.get(question_key)
    if question:
        await send_pdf(callback_query.from_user.id, question_key)  # Отправляем PDF-файл с именем вопроса


# Обработка нажатия на кнопку "Необходимые сервисы"
@dp.message_handler(lambda message: message.text == "Необходимые сервисы")
async def process_services_callback(message: types.Message):
    inline_keyboard_markup = types.InlineKeyboardMarkup(row_width=1)
    url_buttons = {
        "ROBOFOREX": "https://my.roboforex.com/en/?a=eerz",
        "Forex-Box": "https://my.forex-box.com/aff.php?aff=11631",
        "Binance": "https://www.binance.info/ru/https://accounts.binance.info/register?ref=205514549",
        "Наш Telegram канал": "https://t.me/byasha_international",
        "Администратор": "https://t.me/pipisods"
    }
    for text, url in url_buttons.items():
        inline_keyboard_markup.add(types.InlineKeyboardButton(text, url=url))

    await bot.send_message(message.from_user.id, "Необходимые сервисы:", reply_markup=inline_keyboard_markup)


@dp.callback_query_handler(lambda query: query.data == "faq")
async def open_faq(callback_query: types.CallbackQuery):
    await callback_query.answer()
    inline_keyboard_markup = types.InlineKeyboardMarkup(row_width=1)
    inline_keyboard_markup.add(types.InlineKeyboardButton("Часто задаваемые вопросы", callback_data="faq_questions"))
    inline_keyboard_markup.add(
        types.InlineKeyboardButton("Установка торгового помощника", callback_data="faq_assistant"))

    await bot.send_message(callback_query.from_user.id, "Выберите раздел:", reply_markup=inline_keyboard_markup)


async def send_answer(chat_id, question, answer):
    await bot.send_message(chat_id, f"{question}\n\n{answer}")


# Обработчики кнопок
@dp.message_handler(lambda message: message.text in ["Торговые советники", "FAQ", "Новости недели"])
async def handle_button_click(message: types.Message):
    if message.text == "Торговые советники":
        await send_robot_options(message)
    elif message.text == "FAQ":
        inline_keyboard_markup = types.InlineKeyboardMarkup(row_width=1)
        inline_keyboard_markup.add(
            types.InlineKeyboardButton("Часто задаваемые вопросы", callback_data="faq_questions"))
        inline_keyboard_markup.add(
            types.InlineKeyboardButton("Установка торгового помощника", callback_data="faq_assistant"))

        await bot.send_message(message.from_user.id, "Выберите раздел:", reply_markup=inline_keyboard_markup)
    elif message.text == "Новости недели":
        today = datetime.today()
        monday = today - timedelta(days=today.weekday())
        sunday = today + timedelta(days=(6 - today.weekday()))

        events = await fetch_calendar_events(monday, sunday)
        if events is not None:
            msg = format_calendar_message(events)
            await message.answer(msg, parse_mode="HTML")
        else:
            await message.answer("Ошибка при получении данных. Попробуйте позже.")


@dp.message_handler(lambda message: message.text.lower() == "расчет профита")
async def start_profit_calculation(message: types.Message, state: FSMContext):
    await ask_for_amount(message)


if __name__ == '__main__':
    # Set up polling
    dp.middleware.setup(LoggingMiddleware())
    executor.start_polling(dp, skip_updates=True)
