from aiogram.fsm.state import StatesGroup, State

class CreativeStates(StatesGroup):
    wait_prompt = State()
    wait_photo = State()
    confirm = State()

class RefundStates(StatesGroup):
    wait_comment = State()

class AdminBroadcastStates(StatesGroup):
    wait_text = State()
    wait_media = State()
    confirm = State()

class AdminPostStates(StatesGroup):
    wait_text = State()
    wait_media = State()
    confirm = State()

class AdminCreditsStates(StatesGroup):
    wait_tg_id = State()
    wait_amount = State()
