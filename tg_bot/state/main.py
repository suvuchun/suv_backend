from aiogram.fsm.state import StatesGroup, State


class LanguageState(StatesGroup):
    language = State()

class MenuState(StatesGroup):
    menu = State()
    bonus=State()
    contact=State()
    rules=State()
    categories=State()
    basked=State()

class AskInfo(StatesGroup):
    get_number = State()
    address = State()
    bottle=State()
    note=State()