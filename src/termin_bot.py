import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import CommandStart
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.dispatcher.router import Router
import asyncpg
from aiogram import types
from dotenv import load_dotenv
import os


API_TOKEN = os.getenv('TELEGRAM_TOKEN')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
SSH_HOST = os.getenv('SSH_HOST')
SSH_USERNAME = os.getenv('SSH_USERNAME')
SSH_KEY = os.getenv('SSH_KEY')

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
router = Router()

class Form(StatesGroup):
    first_name = State()
    last_name = State()
    date_of_birth = State()
    address = State()
    email = State()
    residence_title_number = State()
    residence_title_valid_till = State()

# Создание таблицы в базе данных
async def create_db():
    conn = await asyncpg.connect(user=DB_USER, password=DB_PASSWORD, database=DB_NAME, host=DB_HOST, port=DB_PORT)
    try:
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS termins (
                id SERIAL PRIMARY KEY,
                user_id BIGINT,
                chat_id BIGINT,
                first_name VARCHAR(255),
                last_name VARCHAR(255),
                date_of_birth VARCHAR(255),
                address VARCHAR(255),
                email VARCHAR(255),
                residence_title_number VARCHAR(255),
                residence_title_valid_till VARCHAR(255),
                processed BOOLEAN DEFAULT FALSE
            )
        ''')
        print("Table 'termins' is created or already exists.")
    except Exception as e:
        print(f"An error occurred while creating the table: {e}")
    finally:
        await conn.close()

async def save_to_database(user_id, chat_id, data):
    conn = await asyncpg.connect(user=DB_USER, password=DB_PASSWORD, database=DB_NAME, host=DB_HOST, port=DB_PORT)
    try:
        await conn.execute('''
            INSERT INTO termins (
                user_id, chat_id, first_name, last_name, date_of_birth, address, email, residence_title_number, residence_title_valid_till, processed
            ) VALUES($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
        ''', user_id, chat_id, data['first_name'], data['last_name'], data['date_of_birth'], data['address'], data['email'], data['residence_title_number'], data['residence_title_valid_till'], False)
        print(f"Data saved successfully for user {user_id}.")
    except Exception as e:
        print(f"An error occurred while saving data for user {user_id}: {e}")
    finally:
        await conn.close()

@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.set_state(Form.first_name)
    await message.answer("Hello! What's your first name?")

@router.message(Form.first_name)
async def process_first_name(message: types.Message, state: FSMContext):
    await state.update_data(first_name=message.text)
    await state.set_state(Form.last_name)
    await message.answer("What's your last name?")

@router.message(Form.last_name)
async def process_last_name(message: types.Message, state: FSMContext):
    await state.update_data(last_name=message.text)
    await state.set_state(Form.date_of_birth)
    await message.answer("What's your date of birth? (YYYY-MM-DD)")

@router.message(Form.date_of_birth)
async def process_date_of_birth(message: types.Message, state: FSMContext):
    await state.update_data(date_of_birth=message.text)
    await state.set_state(Form.address)
    await message.answer("What's your address?")

@router.message(Form.address)
async def process_address(message: types.Message, state: FSMContext):
    await state.update_data(address=message.text)
    await state.set_state(Form.email)
    await message.answer("What's your email address?")

@router.message(Form.email)
async def process_email(message: types.Message, state: FSMContext):
    await state.update_data(email=message.text)
    await state.set_state(Form.residence_title_number)
    await message.answer("What's your residence title number?")

@router.message(Form.residence_title_number)
async def process_residence_title_number(message: types.Message, state: FSMContext):
    await state.update_data(residence_title_number=message.text)
    await state.set_state(Form.residence_title_valid_till)
    await message.answer("Until when is your residence title valid? (YYYY-MM-DD)")

@router.message(Form.residence_title_valid_till)
async def process_residence_title_valid_till(message: types.Message, state: FSMContext):
    data = await state.get_data()
    data['residence_title_valid_till'] = message.text
    user_id = message.from_user.id
    chat_id = message.chat.id
    await save_to_database(user_id, chat_id, data)
    await message.answer(f"Thank you, {data['first_name']}! Your data has been saved. We will notify you once we process it.")
    await state.clear()

async def main():
    await create_db()
    dp = Dispatcher(storage=storage)
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())