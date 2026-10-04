from asyncpg import ForeignKeyViolationError
from connection import connection


async def add_place(author_id, title, city, description, photo_file_id):
	conn = await connection()
	if conn is None:
		return None

	try:
		place_id = await conn.fetchval('''
		insert into places(author_id,title,city,description,photo_file_id)
		values($1,$2,$3,$4,$5)
		returning id
		''', author_id, title, city, description, photo_file_id)
		print('место добавлено')
		return place_id
	except Exception as err:
		print('у вас не добавлено место ошибка в:', err)
		return None
	finally:
		await conn.close()


async def show_places():
	conn = await connection()
	if conn is None:
		return None

	try:
		places = await conn.fetch('''
		select id,title,city from places order by id
		''')
		return places
	except Exception as err:
		print('у вас не показан каталог ошибка в:', err)
		return None
	finally:
		await conn.close()


async def get_place(place_id):
	conn = await connection()
	if conn is None:
		return None

	try:
		place = await conn.fetchrow('''
		select id,author_id,title,city,description,photo_file_id from places
		where id=$1
		''', place_id)
		return place
	except Exception as err:
		print('у вас не открыто место ошибка в:', err)
		return None
	finally:
		await conn.close()


async def show_city_places(city):
	conn = await connection()
	if conn is None:
		return None

	try:
		places = await conn.fetch('''
		select id,title,city from places where lower(city)=lower($1) order by id
		''', city)
		return places
	except Exception as err:
		print('у вас не показаны места города ошибка в:', err)
		return None
	finally:
		await conn.close()


async def add_saved(user_id, place_id):
	conn = await connection()
	if conn is None:
		return None

	try:
		saved_id = await conn.fetchval('''
		insert into saved_places(user_id,place_id) values($1,$2)
		on conflict(user_id,place_id) do nothing
		returning id
		''', user_id, place_id)
		if saved_id is None:
			return 'exists'
		print('место сохранено')
		return 'saved'
	except ForeignKeyViolationError:
		return 'not_found'
	except Exception as err:
		print('у вас не сохранено место ошибка в:', err)
		return None
	finally:
		await conn.close()


async def edit_visited(user_id, place_id):
	conn = await connection()
	if conn is None:
		return None

	try:
		updated = await conn.fetchval('''
		update saved_places set is_visited=true
		where user_id=$1 and place_id=$2 and is_visited=false
		returning id
		''', user_id, place_id)
		if updated is not None:
			print('место отмечено посещённым')
			return 'ok'

		saved = await conn.fetchrow('''
		select is_visited from saved_places where user_id=$1 and place_id=$2
		''', user_id, place_id)
		if saved is None:
			return 'not_saved'
		return 'already'
	except Exception as err:
		print('у вас не отмечено место ошибка в:', err)
		return None
	finally:
		await conn.close()


async def delete_saved(user_id, place_id):
	conn = await connection()
	if conn is None:
		return None

	try:
		deleted = await conn.fetchval('''
		delete from saved_places where user_id=$1 and place_id=$2
		returning id
		''', user_id, place_id)
		if deleted is None:
			return 'not_saved'
		print('место убрано из списка')
		return 'ok'
	except Exception as err:
		print('у вас не убрано место ошибка в:', err)
		return None
	finally:
		await conn.close()


async def show_my_places(user_id):
	conn = await connection()
	if conn is None:
		return None

	try:
		places = await conn.fetch('''
		select p.id,p.title,p.city,sp.is_visited from saved_places sp
		join places p on p.id=sp.place_id
		where sp.user_id=$1 order by sp.saved_at desc,sp.id desc
		''', user_id)
		return places
	except Exception as err:
		print('у вас не показаны мои места ошибка в:', err)
		return None
	finally:
		await conn.close()


async def show_visited(user_id):
	conn = await connection()
	if conn is None:
		return None

	try:
		places = await conn.fetch('''
		select p.id,p.title,p.city,sp.is_visited from saved_places sp
		join places p on p.id=sp.place_id
		where sp.user_id=$1 and sp.is_visited=true
		order by sp.saved_at desc,sp.id desc
		''', user_id)
		return places
	except Exception as err:
		print('у вас не показаны посещённые места ошибка в:', err)
		return None
	finally:
		await conn.close()


async def get_my_place(user_id, place_id):
	conn = await connection()
	if conn is None:
		return None

	try:
		place = await conn.fetchrow('''
		select p.id,p.title,p.city,sp.is_visited from saved_places sp
		join places p on p.id=sp.place_id
		where sp.user_id=$1 and sp.place_id=$2
		''', user_id, place_id)
		return place
	except Exception as err:
		print('у вас не открыто моё место ошибка в:', err)
		return None
	finally:
		await conn.close()