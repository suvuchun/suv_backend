from bot.models import *
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
from django.core.paginator import Paginator
from aiogram import types
from tg_bot.buttons.text import *


def get_language_inline_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=uz_text, callback_data="lang_uz"),
                InlineKeyboardButton(text=ru_text, callback_data="lang_ru"),
            ],

        ]
    )
    return keyboard


def get_address_confirm_keyboard(lang='uz'):
    if lang == 'uz':
        text1 = "✅ Manzil o‘zgarmadi"
        text2 = ortga
    elif lang == 'ru':
        text1 = "✅ Адрес не изменился"
        text2 = nazad
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=text1, callback_data="address_confirmed"),
             InlineKeyboardButton(text=text2, callback_data="back"), ],
        ]
    )


def get_note(lang='uz'):
    if lang == 'uz':
        text1 = "⁉️ Izohsiz"
        text2 = ortga
    elif lang == 'ru':
        text1 = "⁉️ Без комментариев"
        text2 = nazad
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=text1, callback_data="note_no"),
             InlineKeyboardButton(text=text2, callback_data="back"), ],
        ]
    )

def get_accept(lang='uz'):
    if lang == 'uz':
        text1 = "✅ Buyurtmani tasdiqlash"
        text2 = ortga
    elif lang == 'ru':
        text1 = "✅ Подтвердить заказ"
        text2 = nazad
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=text1, callback_data="accept_order"),
             InlineKeyboardButton(text=text2, callback_data="back"), ],
        ]
    )


def get_count(lang='uz'):
    builder = InlineKeyboardBuilder()
    for i in range(1, 10):
        builder.button(
            text=str(i),
            callback_data=f"bottle_{i}"
        )
    if lang == 'uz':
        keyboard = InlineKeyboardButton(text="🅾️ Idishlar yo'q", callback_data="bottle_0")
        keyboard2 = InlineKeyboardButton(text=ortga, callback_data="back")
        builder.add(keyboard)
        builder.add(keyboard2)
    elif lang == 'ru':
        keyboard = InlineKeyboardButton(text="🅾️ Нет капсул", callback_data="bottle_0")
        keyboard1 = InlineKeyboardButton(text=nazad, callback_data="back")
        builder.add(keyboard)
        builder.add(keyboard1)
    builder.adjust(3)
    return builder.as_markup()


def get_categories_keyboard(lang='uz'):
    builder = InlineKeyboardBuilder()
    categories = Category.objects.all()
    if lang == 'uz':
        for category in categories:
            builder.button(
                text=category.name,
                callback_data=f"category_{category.id}"
            )
        keyboard = InlineKeyboardButton(text=ortga, callback_data="back")
        builder.add(keyboard)
    elif lang == 'ru':
        for category in categories:
            builder.button(
                text=category.name_ru,
                callback_data=f"category_{category.id}"
            )
        keyboard = InlineKeyboardButton(text=nazad, callback_data="back")
        builder.add(keyboard)

    builder.adjust(2)
    return builder.as_markup()


def products_show(category_id, lang='uz'):
    builder = InlineKeyboardBuilder()
    products = Product.objects.filter(category_id=category_id)
    if lang == 'uz':
        for product in products:
            builder.button(
                text=product.title,
                callback_data=f"product_{product.id}"
            )
        keyboard = InlineKeyboardButton(text=ortga, callback_data="back")
        builder.add(keyboard)
    elif lang == 'ru':
        for product in products:
            builder.button(
                text=product.title_ru,
                callback_data=f"product_{product.id}"
            )
        keyboard = InlineKeyboardButton(text=nazad, callback_data="back")
        builder.add(keyboard)
    builder.adjust(2)
    return builder.as_markup()


def quantity_picker(product_id, lang='uz'):
    builder = InlineKeyboardBuilder()
    for i in range(1, 10):
        builder.button(
            text=str(i),
            callback_data=f"quantity_{product_id}_{i}"
        )
    if lang == 'uz':
        keyboard = InlineKeyboardButton(text=ortga, callback_data="back")
        builder.add(keyboard)
    elif lang == 'ru':
        keyboard = InlineKeyboardButton(text=nazad, callback_data="back")
        builder.add(keyboard)
    builder.adjust(3)
    return builder.as_markup()


def menu(lang='uz'):
    if lang == 'uz':
        text1 = "Mahsulotlar 💧"
        text2 = "Tilni o'zgartirish 🌐"
        text3 = "Buyurtmalarim 📦"
        text4 = "Aksiyalar 🎁"
        text5 = "Biz bilan aloqa ☎️"
        text6 = "Qoidalar 🧾"
        text7 = "Savatcha 🛒"
    elif lang == 'ru':
        text1 = "Продукты 💧"
        text2 = "Изменить язык 🌐"
        text3 = "Мои заказы 📦"
        text4 = "Акции 🎁"
        text5 = "Связь с нами ☎️"
        text6 = "Правила 🧾"
        text7 = "Корзина 🛒"
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=text1, callback_data="menu_products"), ],
            [InlineKeyboardButton(text=text7, callback_data="menu_basked"),
             InlineKeyboardButton(text=text3, callback_data="menu_history"),

             ],
            [InlineKeyboardButton(text=text4, callback_data="menu_bonus"),
             InlineKeyboardButton(text=text5, callback_data="menu_contact"),
             ],
            [InlineKeyboardButton(text=text6, callback_data="menu_rules"),
             InlineKeyboardButton(text=text2, callback_data="menu_lang"),
             ]
        ]

    )
    return keyboard


def back(lang='uz'):
    if lang == 'uz':
        text1 = ortga
    elif lang == 'ru':
        text1 = nazad
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=text1, callback_data="back"), ],
        ]

    )
    return keyboard


def cart_order(lang='uz'):
    if lang == 'uz':
        text1 = "🚖 Buyurtma berish"
        text2 = ortga
    elif lang == 'ru':
        text1 = "🚖 Заказать"
        text2 = nazad
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=text1, callback_data="cart_order"),
             InlineKeyboardButton(text=text2, callback_data="back"), ],
        ]

    )
    return keyboard


def cart_buttons(lang='uz'):
    if lang == 'uz':
        text1 = "🚖 Buyurtma berish"
        text2 = "🗑 Savatni tozalash"
        text3 = ortga
    elif lang == 'ru':
        text1 = "🚖 Заказать"
        text2 = "🗑 Очистить корзину"
        text3 = nazad
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=text1, callback_data="cart_order"),
             InlineKeyboardButton(text=text2, callback_data="cart_clear"), ],
            [InlineKeyboardButton(text=text3, callback_data="back"), ]
        ]

    )
    return keyboard

def admin_btn(lang='uz'):
    if lang=='uz':
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[  InlineKeyboardButton(text="Tilni o'zgartirish 🌐", callback_data="menu_lang")]])

    elif lang=='ru':
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="Изменить язык 🌐",callback_data="menu_lang")]]
        )
    else:
        keyboard=None
    return keyboard
