from aiogram.filters import Command, CommandObject
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram import Router, types
from serivises import *
from keybord import *

router = Router()


class AddPlace(StatesGroup):
	title = State()
	city = State()
	description = State()
	photo = State()


class CitySearch(StatesGroup):
	city = State()


def parse_id(text):
	text = (text or '').strip()
	if not text.isascii() or not text.isdigit():
		return None
	number = int(text)
	if number <= 0 or number > 2147483647:
		return None
	return number


def clean_spaces(text):
	return ' '.join((text or '').split())


def place_text(place):
	return (
		f'{place["title"]}\n'
		f'Город: {place["city"]}\n\n'
		f'{place["description"]}\n\n'
		f'ID: {place["id"]}'
	)


def list_text(place):
	return f'#{place["id"]} {place["title"]}\nГород: {place["city"]}'


def my_text(place):
	status = 'посещено' if place['is_visited'] else 'не посещено'
	return list_text(place) + f'\nСтатус: {status}'


async def send_card(bot, chat_id, place):
	try:
		await bot.send_photo(
			chat_id,
			photo=place['photo_file_id'],
			caption=place_text(place),
			reply_markup=card_keyboard(place['id'])
		)
	except TelegramBadRequest as err:
		print('у вас не отправлено фото ошибка в:', err)
		await bot.send_message(
			chat_id,
			place_text(place) + '\n\n(фото сейчас недоступно)',
			reply_markup=card_keyboard(place['id'])
		)


@router.message(Command('add_place'))
async def add_place_handler(message: types.Message, state: FSMContext):
	await state.clear()
	await state.set_state(AddPlace.title)
	await message.answer('Введите название места (отмена: /cancel):')


@router.message(Command('cancel'))
async def cancel_handler(message: types.Message, state: FSMContext):
	if await state.get_state() is None:
		await message.answer('Сейчас нет активного ввода. Отменять нечего.', reply_markup=knop)
		return

	await state.clear()
	await message.answer('Ввод отменён. Ничего не сохранено.', reply_markup=knop)


@router.message(Command('places'))
async def places_handler(message: types.Message):
	places = await show_places()
	if places is None:
		await message.answer('Не удалось получить каталог. Проверьте подключение к БД.', reply_markup=knop)
		return
	if not places:
		await message.answer('В каталоге пока нет мест. Добавьте первое: /add_place', reply_markup=knop)
		return

	await message.answer('Общий каталог мест:')
	for place in places:
		await message.answer(list_text(place), reply_markup=catalog_keyboard(place['id']))


@router.message(Command('place'))
async def place_handler(message: types.Message, command: CommandObject):
	args = (command.args or '').strip()
	if not args:
		await message.answer('Укажите id места. Пример: /place 12', reply_markup=knop)
		return

	place_id = parse_id(args)
	if place_id is None:
		await message.answer('id должен быть положительным числом. Пример: /place 12', reply_markup=knop)
		return

	place = await get_place(place_id)
	if place is None:
		await message.answer(f'Место с id {place_id} не найдено.', reply_markup=knop)
		return

	await send_card(message.bot, message.chat.id, place)


@router.message(Command('my_places'))
async def my_places_handler(message: types.Message):
	places = await show_my_places(message.from_user.id)
	if places is None:
		await message.answer('Не удалось получить ваши места. Проверьте подключение к БД.', reply_markup=knop)
		return
	if not places:
		await message.answer('У вас пока нет сохранённых мест. Откройте /places и нажмите «Сохранить».', reply_markup=knop)
		return

	await message.answer('Ваши сохранённые места:')
	for place in places:
		await message.answer(my_text(place), reply_markup=my_keyboard(place['id'], place['is_visited']))


@router.message(Command('visited'))
async def visited_handler(message: types.Message):
	places = await show_visited(message.from_user.id)
	if places is None:
		await message.answer('Не удалось получить посещённые места. Проверьте подключение к БД.', reply_markup=knop)
		return
	if not places:
		await message.answer('Вы пока не отметили ни одного места как посещённое.', reply_markup=knop)
		return

	await message.answer('Посещённые места:')
	for place in places:
		await message.answer(my_text(place), reply_markup=visited_keyboard(place['id']))


async def send_city_places(message, city):
	if len(city) > 100:
		await message.answer('Название города должно быть не длиннее 100 символов.', reply_markup=knop)
		return
	places = await show_city_places(city)
	if places is None:
		await message.answer('Не удалось получить места города. Проверьте подключение к БД.', reply_markup=knop)
		return
	if not places:
		await message.answer(f'В городе «{city}» пока нет мест.', reply_markup=knop)
		return
	await message.answer(f'Места города «{city}»:')
	for place in places:
		await message.answer(list_text(place), reply_markup=catalog_keyboard(place['id']))


@router.message(Command('city'))
async def city_handler(message: types.Message, command: CommandObject, state: FSMContext):
	await state.clear()
	city = clean_spaces(command.args)
	if city:
		await send_city_places(message, city)
		return
	await state.set_state(CitySearch.city)
	await message.answer('Введите название города или отмените ввод через /cancel:')


@router.message(CitySearch.city)
async def process_city_handler(message: types.Message, state: FSMContext):
	city = clean_spaces(message.text)
	if not city or city.startswith('/'):
		await message.answer('Город нужно ввести текстом. Введите город:')
		return
	await state.clear()
	await send_city_places(message, city)


@router.message(AddPlace.title)
async def add_title_handler(message: types.Message, state: FSMContext):
	title = (message.text or '').strip()
	if not title or title.startswith('/'):
		await message.answer('Название нужно ввести текстом. Оно не может быть пустым или командой. Введите название:')
		return
	if len(title) > 150:
		await message.answer('Название должно быть не длиннее 150 символов. Введите его ещё раз:')
		return

	await state.update_data(title=title)
	await state.set_state(AddPlace.city)
	await message.answer('Введите город:')


@router.message(AddPlace.city)
async def add_city_handler(message: types.Message, state: FSMContext):
	city = clean_spaces(message.text)
	if not city or city.startswith('/'):
		await message.answer('Город нужно ввести текстом. Он не может быть пустым или командой. Введите город:')
		return
	if len(city) > 100:
		await message.answer('Название города должно быть не длиннее 100 символов. Введите его ещё раз:')
		return

	await state.update_data(city=city)
	await state.set_state(AddPlace.description)
	await message.answer('Введите описание места:')


@router.message(AddPlace.description)
async def add_description_handler(message: types.Message, state: FSMContext):
	description = (message.text or '').strip()
	if not description or description.startswith('/'):
		await message.answer('Описание нужно ввести текстом. Оно не может быть пустым или командой. Введите описание:')
		return
	if len(description) > 700:
		await message.answer('Описание должно быть не длиннее 700 символов. Введите его ещё раз:')
		return

	await state.update_data(description=description)
	await state.set_state(AddPlace.photo)
	await message.answer('Отправьте фото места (обычным фото, не файлом):')


@router.message(AddPlace.photo)
async def add_photo_handler(message: types.Message, state: FSMContext):
	if not message.photo:
		await message.answer('Нужна фотография. Отправьте фото места обычным фото, не файлом:')
		return

	data = await state.get_data()
	place_id = await add_place(
		message.from_user.id,
		data['title'],
		data['city'],
		data['description'],
		message.photo[-1].file_id
	)
	if place_id is None:
		await message.answer('Не удалось сохранить место. Проверьте подключение к БД и отправьте фото ещё раз:')
		return

	await state.clear()
	await message.answer(f'Место добавлено! Его id: {place_id}', reply_markup=knop)