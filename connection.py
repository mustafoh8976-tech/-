from dotenv import load_dotenv
import asyncpg
import os


load_dotenv()


async def connection():
	try:
		conn = await asyncpg.connect(
			user=os.getenv('DB_USER'),
			password=os.getenv('DB_PASSWORD'),
			port=int(os.getenv('DB_PORT')),
			host=os.getenv('DB_HOST'),
			database=os.getenv('DB_NAME')
		)
		print('подключено в БД')
		return conn
	except Exception as err:
		print('у вас ошибка в БД:', err)