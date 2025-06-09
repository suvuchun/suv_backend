from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_contact_keyboard(language='uz'):
    if language == 'uz':
        text = "📞 Raqamni yuborish"
    elif language == 'ru':
        text = "📞 Отправить номер"
    else:
        text = "📞 Send phone number"

    contact_button = KeyboardButton(text=text, request_contact=True, )
    design = [[contact_button]]
    return ReplyKeyboardMarkup(keyboard=design, resize_keyboard=True, input_field_placeholder="+998901234567")
def get_location_keyboard(language='uz'):
    if language == 'uz':
        text = "📍 Lokatsiyamni yuborish"
    elif language == 'ru':
        text = "📍 Отправить мою локацию"
    else:
        text = "📞 Send phone number"

    contact_button = KeyboardButton(text=text, request_location=True)
    design = [[contact_button]]
    return ReplyKeyboardMarkup(keyboard=design, resize_keyboard=True)
