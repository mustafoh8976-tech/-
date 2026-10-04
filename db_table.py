from connection import connection


async def create_table():
	conn = await connection()
	if conn is None:
		return False

	try:
		await conn.execute('''
		create table if not exists places(
			id serial primary key,
			author_id bigint not null,
			title varchar(150) not null check (length(trim(title)) > 0),
			city varchar(100) not null check (length(trim(city)) > 0),
			description text not null check (length(trim(description)) > 0),
			photo_file_id text not null check (length(photo_file_id) > 0)
		);
		create table if not exists saved_places(
			id serial primary key,
			user_id bigint not null,
			place_id integer not null references places(id) on delete cascade,
			is_visited boolean not null default false,
			saved_at timestamp not null default now(),
			unique(user_id, place_id)
		);
		create index if not exists idx_places_city on places(lower(city));
		create index if not exists idx_saved_places_user on saved_places(user_id);
		''')
		print('таблицы созданы')
		return True
	except Exception as error:
		print('у вас не созданы таблицы ошибка в:', error)
		return False
	finally:
		await conn.close()