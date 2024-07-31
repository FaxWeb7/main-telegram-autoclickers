import asyncio
from bot.core import launcher
from bot.utils.logger import log

async def main():
	await launcher.start()


if __name__ == '__main__':
	try:
		asyncio.run(main())
	except KeyboardInterrupt:
		log.info("Bot stopped by user")