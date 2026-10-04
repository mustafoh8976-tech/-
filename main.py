from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher, Router, types
from callbeck import router as callback_router
from aiogram.fsm.context import FSMContext
from states import router as state_router
from aiogram.filters import Command
from db_table import create_table
from dotenv import load_dotenv
from keybord import knop
import asyncio
import os


router = Router()


@router.message(Command('start'))
async def starts(message: types.Message, state: FSMContext):
	await state.clear()
	await message.answer('''Привет, я бот для путешественников.
Здесь можно добавлять интересные места с фото и вести свой список: что сохранить и где уже побывал.
Команды:
/add_place - добавить место
/places - общий каталог мест
/place id - фото и описание места
/my_places - мои сохранённые места
/visited - места, где я уже был
/city город - места выбранного города
/cancel - отменить ввод
/help - справка
''', reply_markup=knop)


@router.message(Command('help'))
async def helps(message: types.Message):
	await message.answer('''Вот что я умею:
/start - начать работу со мной
/help - помощь по командам
/add_place - добавить место: название, город, описание и фото по шагам
/places - общий каталог, у каждого места кнопки «Подробнее» и «Сохранить»
/place id - показать фото и описание, пример: /place 12
/my_places - ваши сохранённые места со статусами
/visited - только посещённые места
/city город - места города, пример: /city Нью Йорк
/cancel - отменить текущий ввод
Как пользоваться:
1. Откройте /places и нажмите «Сохранить» у места, которое понравилось
2. В /my_places нажмите «Посетил», когда побываете там
3. «Убрать» удаляет место только из вашего списка, в каталоге оно остаётся
''', reply_markup=knop)


async def main():
	load_dotenv()
	token = os.getenv('BOT_TOKEN')
	if not token:
		print('у вас не указан BOT_TOKEN в файле .env')
		return

	await create_table()
	bot = Bot(token=token)
	dp = Dispatcher(storage=MemoryStorage())
	dp.include_router(router)
	dp.include_router(state_router)
	dp.include_router(callback_router)
	print('Start bot')
	await dp.start_polling(bot)


if __name__ == '__main__':
	asyncio.run(main())