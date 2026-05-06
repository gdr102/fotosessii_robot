from aiogram.fsm.state import StatesGroup, State

class CreativeStates(StatesGroup):
    wait_prompt = State()
    wait_photo = State()
    confirm = State()

class RefundStates(StatesGroup):
    wait_comment = State()
