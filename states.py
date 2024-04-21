from aiogram.fsm.state import StatesGroup, State


class DialogState(StatesGroup):
    talking = State()
    switching = State()
    guest = State()
