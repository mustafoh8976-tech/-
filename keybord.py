from aiogram.types import InlineKeyboardButton,InlineKeyboardMarkup,KeyboardButton,ReplyKeyboardMarkup


knop = ReplyKeyboardMarkup(
	keyboard=[
		[KeyboardButton(text='/places'), KeyboardButton(text='/my_places')],
		[KeyboardButton(text='/visited'), KeyboardButton(text='/add_place')],
		[KeyboardButton(text='/help')]
	],
	resize_keyboard=True
)


def catalog_keyboard(place_id):
	keyboard = InlineKeyboardMarkup(
		inline_keyboard=[
			[
				InlineKeyboardButton(text='Подробнее', callback_data=f'place:show:{place_id}'),
				InlineKeyboardButton(text='⭐ Сохранить', callback_data=f'place:save:{place_id}')
			]
		]
	)
	return keyboard


def my_keyboard(place_id, is_visited):
	row = []
	if not is_visited:
		row.append(InlineKeyboardButton(text='✅ Посетил', callback_data=f'place:visit:{place_id}'))
	row.append(InlineKeyboardButton(text='🗑 Убрать', callback_data=f'place:remove:{place_id}'))
	keyboard = InlineKeyboardMarkup(
		inline_keyboard=[
			[InlineKeyboardButton(text='Подробнее', callback_data=f'place:show:{place_id}')],
			row
		]
	)
	return keyboard


def visited_keyboard(place_id):
	keyboard = InlineKeyboardMarkup(
		inline_keyboard=[
			[
				InlineKeyboardButton(text='Подробнее', callback_data=f'place:show:{place_id}'),
				InlineKeyboardButton(text='🗑 Убрать', callback_data=f'place:remove:{place_id}')
			]
		]
	)
	return keyboard


def card_keyboard(place_id):
	keyboard = InlineKeyboardMarkup(
		inline_keyboard=[
			[
				InlineKeyboardButton(text='⭐ Сохранить', callback_data=f'place:save:{place_id}'),
				InlineKeyboardButton(text='✅ Посетил', callback_data=f'place:visit:{place_id}'),
				InlineKeyboardButton(text='🗑 Убрать', callback_data=f'place:remove:{place_id}')
			]
		]
	)
	return keyboard