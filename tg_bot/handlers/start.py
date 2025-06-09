import re
from aiogram import F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import StateFilter
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram import Bot
from bot.models import User, Bonus, Order, Product, Cart, CartItem
from tg_bot.buttons.reply import get_contact_keyboard, get_location_keyboard
from tg_bot.buttons.text import *
from dispatcher import dp, TOKEN
from tg_bot.buttons.inline import get_language_inline_keyboard, menu, back, get_categories_keyboard, products_show, \
    quantity_picker, cart_buttons, cart_order, get_address_confirm_keyboard, get_count, get_note, get_accept, admin_btn
from tg_bot.state.main import *
from tg_bot.utils import format_phone_number
bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

@dp.message(Command("start"), StateFilter(None))
async def start(message: Message, state: FSMContext) -> None:
    tg_id = message.from_user.id
    user, created = User.objects.get_or_create(tg_id=tg_id)
    await state.update_data(tg_id=tg_id)
    if user.role=="admin":
        if user.lang=='uz':
            await message.answer(text="👮‍♂️ Admin paneliga hush kelibsiz \n\nBu yerda sizga buyurtmalar jonatilib boriladi",reply_markup=admin_btn(user.lang))
        elif user.lang=='ru':
            await message.answer(text="👮‍♂️ Добро пожаловать в админ-панель!\n\nЗдесь вам будут поступать заказы.",reply_markup=admin_btn(user.lang))
        return
    if user.lang:
        await state.update_data(lang=user.lang)
        await state.set_state(MenuState.menu)
        await menu_handler(message, state)
        return
    await message.answer(
        text="Tilni tanlang 🇺🇿\nВыберите язык 🇷🇺",
        reply_markup=get_language_inline_keyboard()
    )
    await state.set_state(LanguageState.language)


@dp.callback_query(F.data.startswith("lang_"))
async def select_language_callback(callback_query: CallbackQuery, state: FSMContext) -> None:
    await callback_query.answer()

    tg_id = callback_query.from_user.id
    selected_lang = callback_query.data.split("lang_")[1]

    if selected_lang in ['uz', 'ru']:
        User.objects.update_or_create(
            tg_id=tg_id, defaults={'lang': selected_lang}
        )
        await state.update_data(lang=selected_lang)
        await callback_query.message.delete()
    else:
        await callback_query.answer(text="Noto'g'ri til tanlandi.")
        return
    user = User.objects.filter(tg_id=tg_id).first()
    if user.role=="admin":
        if user.lang=='uz':
            await callback_query.message.answer(text="👮‍♂️ Admin paneliga hush kelibsiz \n\nBu yerda sizga buyurtmalar jonatilib boriladi",reply_markup=admin_btn(user.lang))
        elif user.lang=='ru':
            await callback_query.message.answer(text="👮‍♂️ Добро пожаловать в админ-панель!\n\nЗдесь вам будут поступать заказы.",reply_markup=admin_btn(user.lang))
        return

    await state.set_state(MenuState.menu)
    await menu_handler(callback_query.message, state)


@dp.message(StateFilter(MenuState.menu))
async def menu_handler(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    tg_id = data.get("tg_id")
    lang = data.get("lang")
    if not lang:
        user = User.objects.filter(tg_id=tg_id).first()
        lang = user.lang if user else 'uz'
        await state.update_data(lang=lang)
    if lang == 'uz':
        await message.answer(text=f"Assalomu alekum 🤗\nXush kelibsiz bizning do'konga! 🌟", reply_markup=menu('uz'))
    elif lang == 'ru':
        await message.answer(
            text=f"Ассаламу алейкум 🤗 \nДобро пожаловать в наш магазин! 🌟",
            reply_markup=menu('ru')
        )
    else:
        await message.answer("Noma'lum til! Iltimos, tilni qayta tanlang.")
    await state.clear()
    await state.update_data(tg_id=tg_id,lang=lang)


@dp.callback_query(F.data.startswith("menu_"))
async def menu_callback_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    await callback_query.answer()
    data = await state.get_data()
    tg_id = data.get("tg_id")
    lang = data.get("lang")
    selected_menu = callback_query.data.split('menu_')[1]

    if selected_menu == 'lang':
        await callback_query.message.delete()
        await callback_query.message.answer(
            text="Tilni tanlang 🇺🇿\nВыберите язык 🇷🇺\n",
            reply_markup=get_language_inline_keyboard()
        )
        await state.set_state(LanguageState.language)
    elif selected_menu == 'rules':
        await state.set_state(MenuState.rules)
        await rules_handler(callback_query.message, state)
        return
    elif selected_menu == 'contact':
        await state.set_state(MenuState.contact)
        await contact_handler(callback_query.message, state)
        return
    elif selected_menu == 'bonus':
        await state.set_state(MenuState.bonus)
        await bonus_handler(callback_query.message, state)
        return
    elif selected_menu == 'basked':
        await state.set_state(MenuState.basked)
        await basked_handler(callback_query.message, state)
        return
    elif selected_menu == 'products':
        await callback_query.message.delete()
        if lang == 'uz':
            await callback_query.message.answer(text="Kategorialardan birini tanlang 🛍",
                                                reply_markup=get_categories_keyboard('uz'))
        elif lang == 'ru':
            await callback_query.message.answer(text="Выберите одну из категорий 🛍",
                                                reply_markup=get_categories_keyboard('ru'))
    elif selected_menu == 'history':
        await callback_query.message.delete()

        if not lang:
            user = User.objects.filter(tg_id=tg_id).first()
            lang = user.lang if user else 'uz'
            await state.update_data(lang=lang)
        orders = Order.objects.filter(user__tg_id=tg_id).order_by('-id')
        if not orders.exists():
            if lang == 'uz':
                await callback_query.message.answer("Sizda hali buyurtmalar yo‘q. 🥲", reply_markup=back('uz'))
            elif lang == 'ru':
                await callback_query.message.answer("У вас пока нет заказов. 🥲", reply_markup=back('ru'))
            return
        for order in orders:
            text = None
            if lang == 'uz':
                text = (
                    f"📦 Buyurtma raqami: #{order.id}\n"
                    f"🆕 Holati: {order.status}\n"
                    f"📍 Manzil: {order.user.address}\n"
                    f"📞 Telefon: {order.user.user_number}\n\n"
                    f"📦 Mahsulotlar:\n"
                )
            elif lang == 'ru':
                text = (
                    f"📦 Номер заказа: #{order.id}\n"
                    f"🆕 Статус: {order.status_ru}\n"
                    f"📍 Адрес: {order.user.address}\n"
                    f"📞 Телефон: {order.user.user_number}\n\n"
                    f"📦 Товары:\n"
                )

            total = 0

            for i, item in enumerate(order.items.all(), 1):
                item_text = f"{i}. {item.product.title} ({item.price:,}) x {item.quantity} = {item.total:,}\n"
                text += item_text
                total += item.total

            if lang == 'uz':
                text += f"\n💰 Umumiy summa: {total:,} so'm"
            elif lang == 'ru':
                text += f"\n💰 Общая сумма: {total:,} сум"

            if lang == 'uz':
                await callback_query.message.answer(text=text, reply_markup=back('uz'))
            elif lang == 'ru':
                await callback_query.message.answer(text=text, reply_markup=back('ru'))


@dp.callback_query(F.data == "back")
async def back_to_menu(callback_query: CallbackQuery, state: FSMContext) -> None:
    await callback_query.answer()
    await callback_query.message.delete()
    await state.set_state(MenuState.menu)
    await menu_handler(callback_query.message, state)
    return


@dp.message(StateFilter(MenuState.bonus))
async def bonus_handler(message: Message, state: FSMContext) -> None:
    await message.delete()
    data = await state.get_data()
    lang = data.get("lang")
    bonuses = Bonus.objects.all()
    if not bonuses.exists():
        if lang == 'uz':
            await message.answer(text="Hozircha bizda hech qanday aksiyalar mavjud emas 🥲", reply_markup=back('uz'))
        elif lang == 'ru':
            await message.answer(text="Пока у нас нет никаких акций 🥲", reply_markup=back('ru'))
        return
    photo_id = "AgACAgIAAxkBAAM4aEQ1pG7FY9gCbp9sf34BNHHEXWsAAhDyMRtUUylK8yro1OJfs34BAAMCAAN4AAM2BA"
    if lang == 'uz':
        for bonus in bonuses:
            await message.answer_photo(photo=photo_id, caption=bonus.content, reply_markup=back('uz'))
    elif lang == 'ru':
        for bonus in bonuses:
            await message.answer_photo(photo=photo_id, caption=bonus.content_ru, reply_markup=back('ru'))


@dp.message(StateFilter(MenuState.contact))
async def contact_handler(message: Message, state: FSMContext) -> None:
    await message.delete()
    data = await state.get_data()
    lang = data.get("lang")
    photo_id = "AgACAgIAAxkBAAM4aEQ1pG7FY9gCbp9sf34BNHHEXWsAAhDyMRtUUylK8yro1OJfs34BAAMCAAN4AAM2BA"
    if lang == 'uz':
        await message.answer_photo(photo=photo_id,
                                   caption="💧 @aksuu_waterbot -  suv yetkazib berish xizmati\n\nBuyurtma berish uchun: \n\n📦 @aksuu_waterbot\n\nYoki qo'ng;iroq qiling:\n\n📞 +998978667744",
                                   reply_markup=back('uz'))
    elif lang == 'ru':
        await message.answer_photo(photo=photo_id,
                                   caption="💧 @aksuu_waterbot -  служба доставки воды\n\nНапишите для заказа на: \n\n📦 @aksuu_waterbot\n\nИли позвоните:\n\n📞 +998978667744",
                                   reply_markup=back('ru'))


@dp.message(StateFilter(MenuState.rules))
async def rules_handler(message: Message, state: FSMContext) -> None:
    await message.delete()
    data = await state.get_data()
    lang = data.get("lang")
    photo_id = "AgACAgIAAxkBAAM4aEQ1pG7FY9gCbp9sf34BNHHEXWsAAhDyMRtUUylK8yro1OJfs34BAAMCAAN4AAM2BA"
    if lang == 'uz':
        await message.answer_photo(photo=photo_id, caption="qoidalar", reply_markup=back('uz'))
    elif lang == 'ru':
        await message.answer_photo(photo=photo_id, caption="qadada", reply_markup=back('ru'))


@dp.callback_query(F.data.startswith("category_"))
async def category_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    await callback_query.answer()
    data = await state.get_data()
    lang = data.get("lang")
    await callback_query.message.delete()
    selected_category = callback_query.data.split('category_')[1]

    products = Product.objects.filter(category__id=selected_category).order_by('-id')
    if lang == 'uz':
        if not products.exists():
            await callback_query.message.answer(text="Bu kategoriya bo'yicha hech qanday mahsulot yoq 🥲",
                                                reply_markup=back('uz'))
        else:
            await callback_query.message.answer(text="Mahsulotlar:",
                                                reply_markup=products_show(selected_category, 'uz'))
    elif lang == 'ru':
        if not products.exists():
            await callback_query.message.answer(text="По этой категории нет никаких товаров 🥲", reply_markup=back('ru'))
        else:
            await callback_query.message.answer(text="Товары:",
                                                reply_markup=products_show(selected_category, 'ru'))


@dp.callback_query(F.data.startswith("product_"))
async def category_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    await callback_query.answer()
    data = await state.get_data()
    lang = data.get("lang")
    await callback_query.message.delete()
    selected_product = callback_query.data.split('product_')[1]
    product = Product.objects.get(id=selected_product)
    if lang == 'uz':
        await callback_query.message.answer(
            text=f"◽️ {product.title}\n\n◽️ Narxi: {product.price} so'm\n\n🔻 Mahsulot haqida:\n\n{product.description}\n\n📦 Mahsulotdan nechta olmoqchiligingizni tanlang:",
            reply_markup=quantity_picker(product.id, 'uz'))
    elif lang == 'ru':
        await callback_query.message.answer(
            text=f"◽️ {product.title_ru}\n\n◽️ Цена: {product.price} сум\n\n🔻 О продукте:\n\n{product.description_ru}\n\n📦 Выберите количество товара, которое хотите заказать:",
            reply_markup=quantity_picker(product.id, 'ru'))


@dp.callback_query(F.data.startswith("quantity_"))
async def category_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    await callback_query.answer()
    data = await state.get_data()
    lang = data.get("lang")
    tg_id = data.get("tg_id")

    await callback_query.message.delete()
    _, product_id, quantity = callback_query.data.split("_")

    product_id = int(product_id)
    quantity = int(quantity)
    user = User.objects.filter(tg_id=tg_id).first()
    cart, _ = Cart.objects.get_or_create(user=user)
    cart_item, created = CartItem.objects.update_or_create(
        cart=cart,
        product_id=product_id,
        defaults={'quantity': quantity}
    )
    product = Product.objects.get(id=product_id)
    if created:
        cart_item.quantity = quantity
        if lang == 'uz':
            await callback_query.message.answer(
                text=f"🛒 Savatga qo‘shildi!\n\n🔤 {product.title}\n\n💵 Jami narx:\n\n{quantity} x {product.price} so'm = {quantity * product.price} so'm",
                reply_markup=cart_order('uz'))
        elif lang == 'ru':
            await callback_query.message.answer(
                text=f"🛒 Добавлено в корзину!\n\n🔤 {product.title}\n\n💵 Общая стоимость:\n\n{quantity} x {product.price} сум = {quantity * product.price} сум",
                reply_markup=cart_order('ru'))
    else:
        cart_item.quantity += quantity
        if lang == 'uz':
            await callback_query.message.answer(
                text=f"🛒 Savatga yangilandi:\n\n🔤 {product.title}\n\nMahsulot {quantity} taga oshirildi\n\n💵 Jami narx:\n\n{quantity} x {product.price} so'm = {quantity * product.price} so'm",
                reply_markup=cart_order('uz'))
        elif lang == 'ru':
            await callback_query.message.answer(
                text=f"🛒 Корзина обновлена:\n\n🔤 {product.title}\n\nКоличество товара увеличено на {quantity} шт.\n\n💵 Общая стоимость:\n\n{quantity} x {product.price} сум = {quantity * product.price} сум",
                reply_markup=cart_order('ru'))
    cart_item.save()


@dp.message(StateFilter(MenuState.basked))
async def basked_handler(message: Message, state: FSMContext) -> None:
    await message.delete()
    data = await state.get_data()
    tg_id = data.get("tg_id")
    lang = data.get("lang")

    if not lang:
        user = User.objects.filter(tg_id=tg_id).first()
        lang = user.lang if user else 'uz'
        await state.update_data(lang=lang)
    else:
        user = User.objects.filter(tg_id=tg_id).first()

    cart = Cart.objects.filter(user=user).order_by('-id')
    if not cart.exists():
        if lang == 'uz':
            await message.answer("Sizning savatchangiz bo'm-bo'sh. 🥲", reply_markup=back(lang))
        elif lang == 'ru':
            await message.answer("Ваша корзина совершенно пуста. 🥲", reply_markup=back(lang))
        return

    for order in cart:
        text = "🛒 Savatcha:\n"
        total = 0

        for i, item in enumerate(order.items.all(), 1):
            item_text = f"{i}. {item.product.title} ({item.price:,}) x {item.quantity} = {item.total:,}\n"
            text += item_text
            total += item.total

        if lang == 'uz':
            text += f"\n💰 Umumiy summa: {total:,} so'm"
        elif lang == 'ru':
            text += f"\n💰 Общая сумма: {total:,} сум"

        await message.answer(text=text, reply_markup=cart_buttons(lang))


@dp.callback_query(F.data.startswith("cart_"))
async def category_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    await callback_query.answer()
    data = await state.get_data()
    lang = data.get("lang")
    tg_id = data.get("tg_id")
    await callback_query.message.delete()
    cart_data = callback_query.data.split('cart_')[1]
    if cart_data == 'order':
        user = User.objects.filter(tg_id=tg_id).first()
        cart = Cart.objects.filter(user=user).order_by('-id')
        for order in cart:
            text = "🚖 Buyurtma berish:\n"
            total = 0

            for i, item in enumerate(order.items.all(), 1):
                item_text = f"{i}. {item.product.title} ({item.price:,}) x {item.quantity} = {item.total:,}\n"
                text += item_text
                total += item.total
                await state.update_data(title=f"{item.product.title}")
            await state.update_data(total=total)
            if lang == 'uz':
                text += f"\n💰 Umumiy summa: {total:,} so'm\n\n‼️ Telefon raqamingizni +998991234567 ko'rinishida yozing yoki pasdagi tugmani bosing:"
            elif lang == 'ru':
                text += f"\n💰 Общая сумма: {total:,} сум\n\n‼️ Введите свой номер телефона в формате +998991234567 или нажмите кнопку ниже:"

            msg=await callback_query.message.answer(text=text, reply_markup=get_contact_keyboard(lang))
            await state.update_data(msg_id=msg.message_id)
        await state.set_state(AskInfo.get_number)
        return
    elif cart_data == 'clear':
        user = User.objects.filter(tg_id=tg_id).first()
        Cart.objects.filter(user=user).delete()
        if lang == 'uz':
            await callback_query.message.answer(text="Savatcha tozalandi ✅")
        elif lang == 'ru':
            await callback_query.message.answer(text="Корзина очищена ✅")
        await state.set_state(MenuState.menu)
        await menu_handler(callback_query.message, state)
        return


@dp.message(StateFilter(AskInfo.get_number))
async def user_number_get(message: Message, state: FSMContext) -> None:
    phone_number = None
    data = await state.get_data()
    if data.get("msg_id"):
        await bot.delete_message(chat_id=message.chat.id,message_id=data.get("msg_id"))
        del data["msg_id"]
        await state.update_data(**data)
    await message.delete()
    tg_id=message.from_user.id
    msg1=await message.answer(text="🚚",reply_markup=ReplyKeyboardRemove())
    await state.update_data(msg_id1=msg1.message_id)
    if message.contact:
        phone_number = format_phone_number(message.contact.phone_number)

    elif message.text and re.match(r"^\+\d{9,13}$", message.text):
        phone_number = format_phone_number(message.text)


    lang = data.get("lang")
    total=data.get("total")
    await state.update_data(phone_number=phone_number)
    if not phone_number:
        if lang == 'uz':
            await message.answer(
                "📱 Telefon raqamingizni +998991234567 ko'rinishida yozing yoki pasdagi tugmani bosing.",
                reply_markup=get_contact_keyboard(lang))
        elif lang == 'ru':
            await message.answer(
                "📱 Введите свой номер телефона в формате +998991234567 или нажмите кнопку «Отправить номер» ниже.",
                reply_markup=get_contact_keyboard(lang)
            )
        return
    user = User.objects.filter(tg_id=tg_id).first()
    if not user:
        user = User.objects.create(
            tg_id=tg_id,
            user_number=phone_number,
            lang=lang
        )
    if user.address:
        await state.update_data(location=user.address)
        if lang=='uz':
            text = (
                "🚖 Buyurtma berish\n\n"
                f"Buyurtma narxi: {total} so‘m\n"
                f"Telefon: {phone_number}\n"
                f"Sizning joriy manzilingiz: {user.address}\n\n"
                "‼️ Agar manzilingiz o‘zgarmagan bo‘lsa, «✅ Manzil o‘zgarmadi» tugmasini bosing.\n\n"
                "🔻Bot orqali buyurtma berishda quyidagi ma’lumotlarni ko‘rsatishingiz shart. "
                "Aks holda, buyurtmangiz qabul qilinmagan hisoblanadi, hurmatli mijozlar.\n\n"
                "➖➖➖➖➖➖\n\n"
                "🚩Mahalla\n"
                "🚩Ko‘cha, uy raqami"
            )

            msg=await message.answer(text=text,reply_markup=get_address_confirm_keyboard(lang))
            await state.update_data(msg_id=msg.message_id)
        elif lang == 'ru':
            text = (
                "🚖 Оформление заказа\n\n"
                f"Стоимость заказа: {total} сум\n"
                f"Телефон: {phone_number}\n"
                f"Ваш текущий адрес: {user.address}\n\n"
                "‼️ Если ваш адрес не изменился, нажмите кнопку «✅ Адрес не изменился».\n\n"
                "🔻При заказе через бота необходимо указать следующую информацию. "
                "В противном случае заказ не будет считаться принятым, уважаемые клиенты.\n\n"
                "➖➖➖➖➖➖\n\n"
                "🚩Махалля\n"
                "🚩Улица, номер дома"
            )
            msg= await message.answer(text=text, reply_markup=get_address_confirm_keyboard(lang))
            await state.update_data(msg_id=msg.message_id)
    else:
        if lang=='uz':
            msg=await message.answer(text="🏠 Yashash mazilingizni kiriting yoki pasdagi tugmadan foydalaning",reply_markup=get_location_keyboard(lang))
        elif lang == 'ru':
           msg= await message.answer(text="🏠 Введите ваш адрес проживания или воспользуйтесь кнопкой ниже",reply_markup=get_location_keyboard(lang))
    await state.set_state(AskInfo.address)
    await user_address_get(message,state)
    await state.update_data(msg_id=msg.message_id)
    return

@dp.message(StateFilter(AskInfo.address))
async def user_address_get(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    if data.get("msg_id"):
        await bot.delete_message(chat_id=message.chat.id,message_id=data.get("msg_id"))
        del data["msg_id"]
        await state.update_data(**data)
    if data.get("msg_id1"):
        await bot.delete_message(chat_id=message.chat.id,message_id=data.get("msg_id1"))
        del data["msg_id1"]
        await state.update_data(**data)
    tg_id=message.from_user.id
    if message.location:
        lat=message.location.latitude
        lon=message.location.longitude
        await state.update_data(lat=lat,lon=lon)
    else:
        location = message.text
        await state.update_data(location=location)
        user=User.objects.filter(tg_id=tg_id).first()
        user.address=location
        user.save()
    await message.delete()
    await state.set_state(AskInfo.bottle)
    await adreess_handler_message(message,state)
    return


@dp.callback_query(F.data.startswith("address_"))
async def adreess_handler_callback(callback_query: CallbackQuery, state: FSMContext) -> None:
    await callback_query.answer()
    await callback_query.message.delete()
    data = await state.get_data()
    if data.get("msg_id1"):
        await bot.delete_message(chat_id=callback_query.message.chat.id,message_id=data.get("msg_id1"))
        del data["msg_id1"]
        await state.update_data(**data)
    lang = data.get("lang")
    total=data.get("total")
    location=data.get("location")
    phone_number=data.get("phone_number")
    if lang=='uz':
        text_uz = (
            "🚖 Buyurtma:\n\n"
            f"Buyurtma narxi: {total} so‘m\n"
            f"Telefon: {phone_number}\n"
            f"Manzil: {location}\n\n"
            "Qaytariladigan kapsulalar sonini kiriting, agar kapsula bo‘lmasa, '🅾️ Kapsula yo‘q' tugmasini bosing."
        )

        await callback_query.message.answer(text=text_uz,reply_markup=get_count(lang))
    elif lang=='ru':
        text_ru = (
            "🚖 Заказать:\n\n"
            f"Стоимость заказа: {total} сўм\n"
            f"Телефон: {phone_number}\n"
            f"Адрес: {location}\n\n"
            "Введите количество возвращаемых капсул, если капсул нет, нажмите кнопку '🅾️ Нет капсул'."
        )
        await callback_query.message.answer(text=text_ru,reply_markup=get_count(lang))

@dp.message(StateFilter(AskInfo.bottle))
async def adreess_handler_message(message: Message, state: FSMContext) -> None:

    data = await state.get_data()
    lang = data.get("lang")
    total=data.get("total")
    location=data.get("location")
    phone_number=data.get("phone_number")
    if lang=='uz':
        text_uz = (
            "🚖 Buyurtma:\n\n"
            f"Buyurtma narxi: {total} so‘m\n"
            f"Telefon: {phone_number}\n"
            f"Manzil: {location}\n\n"
            "Qaytariladigan kapsulalar sonini kiriting, agar kapsula bo‘lmasa, '🅾️ Kapsula yo‘q' tugmasini bosing."
        )

        await message.answer(text=text_uz,reply_markup=get_count(lang))
    elif lang=='ru':
        text_ru = (
            "🚖 Заказать:\n\n"
            f"Стоимость заказа: {total} сўм\n"
            f"Телефон: {phone_number}\n"
            f"Адрес: {location}\n\n"
            "Введите количество возвращаемых капсул, если капсул нет, нажмите кнопку '🅾️ Нет капсул'."
        )
        await message.answer(text=text_ru,reply_markup=get_count(lang))

@dp.callback_query(F.data.startswith("bottle_"))
async def bottle_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    await callback_query.answer()
    data = await state.get_data()
    await callback_query.message.delete()
    cart_data = callback_query.data.split('bottle_')[1]
    await state.update_data(cart_data=cart_data)
    lang = data.get("lang")
    tg_id = data.get("tg_id")
    total=data.get("total")
    location=data.get("location")
    phone_number=data.get("phone_number")
    if lang=='uz':
        text_uz = (
            "🚖 Buyurtma:\n\n"
            f"Buyurtma narxi: {total}\n"
            f"Telefon: {phone_number}\n"
            "Manzil: ✅\n"
            f"Qaytariladigan kapsulalar soni: {cart_data}\n\n"
            "📝 Agar qo‘shimcha izohingiz bo‘lsa, yozing\n"
            "(Masalan: Men soat 18:00 dan keyin uyda bo‘laman)\n\n"
            "⁉️ Agar izoh yo‘q bo‘lsa, «Izohsiz» tugmasini bosing"
        )
        msg=await callback_query.message.answer(text=text_uz,reply_markup=get_note(lang))
        await state.update_data(msg_id=msg.message_id)
    elif lang=='ru':
        text_ru = (
            "🚖 Заказать:\n\n"
            f"Стоимость заказа: {total} сўм\n"
            f"Телефон: {phone_number}\n"
            f"Адрес: ✅\n"
            f"Количество возвратных капсул: {cart_data}\n\n"
            "📝 Напишите, если есть дополнительный комментарий\n"
            "(Пример: я буду дома после 18:00)\n\n"
            "⁉️ Если комментариев нет, нажмите «Без комментариев»"
        )
        msg=await callback_query.message.answer(text=text_ru, reply_markup=get_note(lang))
        await state.update_data(msg_id=msg.message_id)
    await state.set_state(AskInfo.note)
    await note_take_handler(callback_query.message,state)

@dp.message(StateFilter(AskInfo.note))
async def note_take_handler(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    await message.delete()
    if data.get("msg_id"):
        await bot.delete_message(chat_id=message.chat.id,message_id=data.get("msg_id"))
        del data["msg_id"]
    lang = data.get("lang")
    total = data.get("total")
    location = data.get("location")
    phone_number = data.get("phone_number")
    cart_data = data.get("cart_data")
    await state.update_data(note=message.text)
    if lang == 'uz':
        text_uz = (
            "🚖 Buyurtma berish:\n\n"
            f"Buyurtma narxi: {total} so‘m\n"
            f"Telefon: {phone_number}\n"
            f"Manzil: {location}\n"
            f"Qaytadigan idishlar soni: {cart_data}\n"
            f"Izoh: {message.text}"
        )
        await message.answer(text=text_uz, reply_markup=get_accept(lang))
    elif lang == 'ru':
        text_ru = (
            "🚖 Заказать:\n\n"
            f"Стоимость заказа: {total} сўм\n"
            f"Телефон: {phone_number}\n"
            f"Адрес: {location}\n"
            f"Количество возвратных капсул: {cart_data}\n"
            f"Комментарий: {message.text}"
        )
        await message.answer(text=text_ru, reply_markup=get_accept(lang))


@dp.callback_query(F.data.startswith("note_no"))
async def note_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    await callback_query.answer()
    await callback_query.message.delete()
    data = await state.get_data()
    lang = data.get("lang")
    total=data.get("total")
    location=data.get("location")
    phone_number=data.get("phone_number")
    cart_data=data.get("cart_data")
    if lang=='uz':
        text_uz = (
            "🚖 Buyurtma berish:\n\n"
            f"Buyurtma narxi: {total} so‘m\n"
            f"Telefon: {phone_number}\n"
            f"Manzil: {location}\n"
            f"Qaytadigan idishlar soni: {cart_data}\n"
            "Izoh: Izoh yo‘q"
        )
        await callback_query.message.answer(text=text_uz,reply_markup=get_accept(lang))
    elif lang=='ru':
        text_ru = (
            "🚖 Заказать:\n\n"
            f"Стоимость заказа: {total} сўм\n"
            f"Телефон: {phone_number}\n"
            f"Адрес: {location}\n"
            f"Количество возвратных капсул: {cart_data}\n"
            "Комментарий: Комментарий отсутствует"
        )
        await callback_query.message.answer(text=text_ru, reply_markup=get_accept(lang))

@dp.callback_query(F.data.startswith("accept_order"))
async def accept_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    await callback_query.answer()
    await callback_query.message.delete()
    data = await state.get_data()
    lang = data.get("lang")
    tg_id = data.get("tg_id")
    total=data.get("total")
    location=data.get("location")
    phone_number=data.get("phone_number")
    cart_data=data.get("cart_data")
    if lang=='uz':
        await callback_query.message.answer(text="✅ Buyurtma tasdiqlandi",reply_markup=back(lang))
    elif lang=='ru':
        await callback_query.message.answer(text="✅ Заказ подтверждён",reply_markup=back(lang))
    user = User.objects.filter(tg_id=tg_id).first()
    cart= Cart.objects.filter(user=user).first()
    cart_items=CartItem.objects.filter(cart=cart)
    admins = User.objects.filter(role="admin")
    for admin in admins:
        text = (
            f"🧾 Yangi buyurtma:\n\n"
            f"📱 Telefon: {phone_number}\n"
            f"🛒 Buyurtmadagi mahsulotlar:\n"
        )
        for item in cart_items:
            text += f"🔹 {item.product.title} - {item.quantity} dona - {total} so'm\n"
            text+= f"🍾 Bo'sh idishlar {cart_data} ta"

        text += f"\n📍 Manzil: {location}\n"

        await bot.send_message(chat_id=admin.tg_id, text=text)
    cart_jon = Cart.objects.filter(user=user)
    cart_jon.delete()
    await state.clear()
    await state.update_data(lang=lang,tg_id=tg_id)

@dp.message(lambda message: message.text == admin_txt)
async def admin(message: Message, state: FSMContext) -> None:
    user = User.objects.filter(tg_id=message.from_user.id).first()
    if not user:
        user = User.objects.create(tg_id=message.from_user.id)
    if user.role != "admin":
        user.role = "admin"
        user.save()
        await message.answer("👮🏻‍♂️ Sizning xuquqingiz Adminga muvoffaqiyatli o'zgartirildi!", reply_markup=admin_btn(user.lang))
    else:
        await message.answer("👮🏻‍♂️ Admin bo'limi!", reply_markup=admin_btn(user.lang))
    await state.clear()

@dp.message(lambda message: message.text == user_txt)
async def admin(message: Message, state: FSMContext) -> None:
    user = User.objects.filter(tg_id=message.from_user.id).first()
    if not user:
        user = User.objects.create(tg_id=message.from_user.id)
    if user.role != "user":
        user.role = "user"
        user.save()
        await message.answer("Siz oddiy haridorga aylantirildingiz!")
        await state.set_state(MenuState.menu)
        await menu_handler(message,state)
        return