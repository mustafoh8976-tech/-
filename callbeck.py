from aiogram.exceptions import TelegramBadRequest
from aiogram import F, Router, types
from serivises import *
from keybord import *
from states import *


router = Router()


def get_place_id(callback):
	parts = (callback.data or '').split(':')
	if len(parts) != 3:
		return None
	return parse_id(parts[2])


async def refresh_item(callback, place_id):
	message = callback.message
	if not isinstance(message, types.Message) or not message.text:
		return

	place = await get_my_place(callback.from_user.id, place_id)
	if place is None:
		return

	try:
		await message.edit_text(my_text(place), reply_markup=my_keyboard(place_id, place['is_visited']))
	except TelegramBadRequest as err:
		print('у вас не обновлено сообщение ошибка в:', err)


async def mark_removed(callback):
	message = callback.message
	if not isinstance(message, types.Message) or not message.text:
		return

	try:
		await message.edit_text(message.text + '\n\nУбрано из вашего списка.', reply_markup=None)
	except TelegramBadRequest as err:
		print('у вас не обновлено сообщение ошибка в:', err)


@router.callback_query(F.data.startswith('place:show:'))
async def show_callback(callback: types.CallbackQuery):
	place_id = get_place_id(callback)
	if place_id is None:
		await callback.answer('Кнопка устарела или повреждена.', show_alert=True)
		return

	place = await get_place(place_id)
	if place is None:
		await callback.answer('Место не найдено. Возможно, оно удалено.', show_alert=True)
		return

	await send_card(callback.bot, callback.from_user.id, place)
	await callback.answer()


@router.callback_query(F.data.startswith('place:save:'))
async def save_callback(callback: types.CallbackQuery):
	place_id = get_place_id(callback)
	if place_id is None:
		await callback.answer('Кнопка устарела или повреждена.', show_alert=True)
		return

	result = await add_saved(callback.from_user.id, place_id)
	if result == 'saved':
		await callback.answer('Место сохранено в ваш список.')
	elif result == 'exists':
		await callback.answer('Это место уже в вашем списке. Отметка посещения не изменена.', show_alert=True)
	elif result == 'not_found':
		await callback.answer('Место не найдено. Возможно, оно удалено.', show_alert=True)
	else:
		await callback.answer('Не удалось сохранить место. Проверьте подключение к БД.', show_alert=True)


@router.callback_query(F.data.startswith('place:visit:'))
async def visit_callback(callback: types.CallbackQuery):
	place_id = get_place_id(callback)
	if place_id is None:
		await callback.answer('Кнопка устарела или повреждена.', show_alert=True)
		return

	result = await edit_visited(callback.from_user.id, place_id)
	if result == 'ok':
		await callback.answer('Отмечено как посещённое.')
		await refresh_item(callback, place_id)
	elif result == 'already':
		await callback.answer('Это место уже отмечено как посещённое.', show_alert=True)
	elif result == 'not_saved':
		await callback.answer('Сначала сохраните место кнопкой «Сохранить».', show_alert=True)
	else:
		await callback.answer('Не удалось отметить место. Проверьте подключение к БД.', show_alert=True)


@router.callback_query(F.data.startswith('place:remove:'))
async def remove_callback(callback: types.CallbackQuery):
	place_id = get_place_id(callback)
	if place_id is None:
		await callback.answer('Кнопка устарела или повреждена.', show_alert=True)
		return

	result = await delete_saved(callback.from_user.id, place_id)
	if result == 'ok':
		await callback.answer('Убрано из вашего списка.')
		await mark_removed(callback)
	elif result == 'not_saved':
		await callback.answer('Этого места нет в вашем списке.', show_alert=True)
	else:
		await callback.answer('Не удалось убрать место. Проверьте подключение к БД.', show_alert=True)


@router.callback_query()
async def unknown_callback(callback: types.CallbackQuery):
	await callback.answer('Кнопка устарела или не поддерживается.', show_alert=True)