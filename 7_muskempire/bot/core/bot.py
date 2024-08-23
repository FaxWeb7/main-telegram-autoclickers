import asyncio, aiohttp, random, math, json, hashlib, traceback
from time import time as time_now
from zoneinfo import ZoneInfo
from datetime import datetime, time
from urllib.parse import unquote
from aiohttp_proxy import ProxyConnector
from better_proxy import Proxy
from pyrogram import Client
from pyrogram.errors import Unauthorized, UserDeactivated, AuthKeyUnregistered
from pyrogram.raw.functions.messages import RequestWebView

from bot.utils.logger import log
from bot.config import config
from bot.utils.functions import calculate_bet, calculate_best_skill, improve_possible, number_short, calculate_tap_power
from .headers import headers

class CryptoBot:
	def __init__(self, tg_client: Client):
		self.session_name = tg_client.name
		self.tg_client = tg_client
		self.user_id = None
		self.api_url = 'https://api.xempire.io'
		self.taps_limit = False
		self.taps_limit_date = ''
		self.errors = 0

	async def get_tg_web_data(self, proxy: str | None) -> dict:
		if proxy:
			proxy = Proxy.from_str(proxy)
			proxy_dict = dict(
				scheme=proxy.protocol,
				hostname=proxy.host,
				port=proxy.port,
				username=proxy.login,
				password=proxy.password
			)
		else:
			proxy_dict = None

		self.tg_client.proxy = proxy_dict

		try:
			if not self.tg_client.is_connected:
				try:
					await self.tg_client.connect()
				except (Unauthorized, UserDeactivated, AuthKeyUnregistered) as error:
					raise RuntimeError(str(error)) from error
			web_view = await self.tg_client.invoke(RequestWebView(
				peer=await self.tg_client.resolve_peer('empirebot'),
				bot=await self.tg_client.resolve_peer('empirebot'),
				platform='android',
				from_bot_menu=True,
				url='https://game.xempire.io/',
				start_param=config.REF_CODE
			))
			auth_url = web_view.url
			tg_web_data = unquote(
				string=auth_url.split('tgWebAppData=', maxsplit=1)[1].split('&tgWebAppVersion', maxsplit=1)[0])
			
			user_hash = tg_web_data[tg_web_data.find('hash=') + 5:]
			self.api_key = user_hash
			if self.tg_client.is_connected:
				await self.tg_client.disconnect()
			
			login_data = {'data': {
					'initData' : tg_web_data,
					'platform' : 'android',
					'chatId' : ''
				}
			}
			return login_data

		except RuntimeError as error:
			raise error

		except Exception as error:
			log.error(f"{self.session_name} | Authorization error: {error}" + (f"\nTraceback: {traceback.format_exc()}" if config.DEBUG_MODE else ""))
			await asyncio.sleep(delay=3)

	async def login(self, json_data: dict) -> bool:
		url = self.api_url + '/telegram/auth'
		try:
			log.info(f"{self.session_name} | Trying to login...")
			self.http_client.headers['Api-Key'] = 'empty'
			await self.set_sign_headers(data=json_data)
			response = await self.http_client.post(url, json=json_data)
			response.raise_for_status()
			response_text = await response.text()
			if config.DEBUG_MODE:
				log.debug(f"{self.session_name} | Login response:\n{response_text}")
			response_json = json.loads(response_text)
			success = response_json.get('success', False)
			if success: return True
			else: return False
		except Exception as error:
			log.error(f"{self.session_name} | Login error: {error}" + (f"\nTraceback: {traceback.format_exc()}" if config.DEBUG_MODE else ""))
			self.errors += 1
			await asyncio.sleep(delay=3)
			return False
	
	async def set_sign_headers(self, data: dict) -> None:
		time_string = str(int(time_now()))
		json_string = json.dumps(data)
		hash_object = hashlib.md5()
		hash_object.update(f"{time_string}_{json_string}".encode('utf-8'))
		hash_string = hash_object.hexdigest()
		self.http_client.headers['Api-Time'] = time_string
		self.http_client.headers['Api-Hash'] = hash_string

	async def get_profile(self, full: bool) -> dict:
		full_url = self.api_url + '/user/data/all'
		after_url = self.api_url + '/user/data/after'
		sync_url = self.api_url + '/hero/balance/sync'
		try:
			if full:
				json_data = {'data': {}}
				await self.set_sign_headers(data=json_data)
				response = await self.http_client.post(full_url, json=json_data)
				response.raise_for_status()
				response_text = await response.text()
				if config.DEBUG_MODE:
					log.debug(f"{self.session_name} | Full profile response:\n{response_text}")
				response_json = json.loads(response_text)
				data = response_json['data']
				lang = data.get('settings', {}).get('lang', 'en')
				json_data = {'data': {'lang': lang}}
				await self.set_sign_headers(data=json_data)
				response = await self.http_client.post(after_url, json=json_data)
				response.raise_for_status()
				response_text = await response.text()
				if config.DEBUG_MODE:
					log.debug(f"{self.session_name} | After profile response:\n{response_text}")
				response_json = json.loads(response_text)
				data.update(response_json['data'])
				return data
			else:
				json_data = {}
				await self.set_sign_headers(data=json_data)
				response = await self.http_client.post(sync_url, json=json_data)
				response.raise_for_status()
				response_text = await response.text()
				if config.DEBUG_MODE:
					log.debug(f"{self.session_name} | Sync profile response:\n{response_text}")
				response_json = json.loads(response_text)
				return response_json['data']
		except aiohttp.ClientResponseError as error:
			if error.status == 401: self.authorized = False
			self.errors += 1
			log.error(f"{self.session_name} | Profile data http error: {error.message}" + (f"\nTraceback: {traceback.format_exc()}" if config.DEBUG_MODE else ""))
			await asyncio.sleep(delay=3)
			return {}
		except Exception as error:
			log.error(f"{self.session_name} | Profile data error: {error}" + (f"\nTraceback: {traceback.format_exc()}" if config.DEBUG_MODE else ""))
			await asyncio.sleep(delay=3)
			return {}

	async def get_offline_bonus(self) -> bool:
		url = self.api_url + '/hero/bonus/offline/claim'
		try:
			json_data = {}
			await self.set_sign_headers(data=json_data)
			response = await self.http_client.post(url, json=json_data)
			response.raise_for_status()
			response_text = await response.text()
			if config.DEBUG_MODE:
				log.debug(f"{self.session_name} | Offline bonus response:\n{response_text}")
			response_json = json.loads(response_text)
			success = response_json.get('success', False)
			if success:
				self.errors = 0
				self.update_level(level=int(response_json['data']['hero']['level']))
				self.balance = int(response_json['data']['hero']['money'])
				self.mph = int(response_json['data']['hero']['moneyPerHour'])
				return True
			else: return False
		except aiohttp.ClientResponseError as error:
			if error.status == 401: self.authorized = False
			self.errors += 1
			log.error(f"{self.session_name} | Offline bonus http error: {error.message}" + (f"\nTraceback: {traceback.format_exc()}" if config.DEBUG_MODE else ""))
			await asyncio.sleep(delay=3)
			return False
		except Exception as error:
			log.error(f"{self.session_name} | Offline bonus error: {error}" + (f"\nTraceback: {traceback.format_exc()}" if config.DEBUG_MODE else ""))
			await asyncio.sleep(delay=3)
			return False

	async def daily_reward(self, index: int) -> bool:
		url = self.api_url + '/quests/daily/claim'
		try:
			json_data = {'data': f"{index}"}
			await self.set_sign_headers(data=json_data)
			response = await self.http_client.post(url, json=json_data)
			response.raise_for_status()
			response_text = await response.text()
			if config.DEBUG_MODE:
				log.debug(f"{self.session_name} | Daily reward response:\n{response_text}")
			response_json = json.loads(response_text)
			success = response_json.get('success', False)
			if success:
				self.errors = 0
				self.update_level(level=int(response_json['data']['hero']['level']))
				self.balance = int(response_json['data']['hero']['money'])
				self.mph = int(response_json['data']['hero']['moneyPerHour'])
				return True
			else: return False
		except aiohttp.ClientResponseError as error:
			if error.status == 401: self.authorized = False
			self.errors += 1
			log.error(f"{self.session_name} | Daily reward http error: {error.message}" + (f"\nTraceback: {traceback.format_exc()}" if config.DEBUG_MODE else ""))
			await asyncio.sleep(delay=3)
			return False
		except Exception as error:
			log.error(f"{self.session_name} | Daily reward error: {str(error)}" + (f"\nTraceback: {traceback.format_exc()}" if config.DEBUG_MODE else ""))
			return False
			
	async def quest_reward(self, quest: str, code:str = None) -> bool:
		url = self.api_url + '/quests/claim'
		try:
			json_data = {'data': [quest, code]}
			await self.set_sign_headers(data=json_data)
			response = await self.http_client.post(url, json=json_data)
			response.raise_for_status()
			response_text = await response.text()
			if config.DEBUG_MODE:
				log.debug(f"{self.session_name} | Quest reward response:\n{response_text}")
			response_json = json.loads(response_text)
			success = response_json.get('success', False)
			if success:
				self.errors = 0
				self.update_level(level=int(response_json['data']['hero']['level']))
				self.balance = int(response_json['data']['hero']['money'])
				self.mph = int(response_json['data']['hero']['moneyPerHour'])
				return True
			else: return False
		except aiohttp.ClientResponseError as error:
			if error.status == 401: self.authorized = False
			self.errors += 1
			log.error(f"{self.session_name} | Quest reward http error: {error.message}" + (f"\nTraceback: {traceback.format_exc()}" if config.DEBUG_MODE else ""))
			await asyncio.sleep(delay=3)
			return False
		except Exception as error:
			log.error(f"{self.session_name} | Quest reward error: {str(error)}" + (f"\nTraceback: {traceback.format_exc()}" if config.DEBUG_MODE else ""))
			return False
	
	async def daily_quest_reward(self, quest: str, code:str = None) -> bool:
		url = self.api_url + '/quests/daily/progress/claim'
		try:
			json_data = {'data': {'quest': quest, 'code': code}}
			await self.set_sign_headers(data=json_data)
			response = await self.http_client.post(url, json=json_data)
			response.raise_for_status()
			response_text = await response.text()
			if config.DEBUG_MODE:
				log.debug(f"{self.session_name} | Daily quest reward response:\n{response_text}")
			response_json = json.loads(response_text)
			success = response_json.get('success', False)
			if success:
				self.errors = 0
				self.update_level(level=int(response_json['data']['hero']['level']))
				self.balance = int(response_json['data']['hero']['money'])
				self.mph = int(response_json['data']['hero']['moneyPerHour'])
				return True
			else: return False
		except aiohttp.ClientResponseError as error:
			if error.status == 401: self.authorized = False
			self.errors += 1
			log.error(f"{self.session_name} | Daily quest reward http error: {error.message}" + (f"\nTraceback: {traceback.format_exc()}" if config.DEBUG_MODE else ""))
			await asyncio.sleep(delay=3)
			return False
		except Exception as error:
			log.error(f"{self.session_name} | Daily quest reward error: {str(error)}" + (f"\nTraceback: {traceback.format_exc()}" if config.DEBUG_MODE else ""))
			return False
	
	async def daily_quests(self) -> None:
		url = self.api_url + '/quests/daily/progress/all'
		try:
			json_data = {}
			await self.set_sign_headers(data=json_data)
			response = await self.http_client.post(url, json=json_data)
			response.raise_for_status()
			response_text = await response.text()
			if config.DEBUG_MODE:
				log.debug(f"{self.session_name} | Daily quests response:\n{response_text}")
			response_json = json.loads(response_text)
			success = response_json.get('success', False)
			if success:
				for name, quest in response_json['data'].items():
					if 'youtube' in name: continue
					if quest['isComplete'] is True and quest['isRewarded'] is False:
						await asyncio.sleep(random.randint(1, 2))
						if await self.daily_quest_reward(quest=name):
							log.success(f"{self.session_name} | Reward for daily quest {name} claimed")
		except aiohttp.ClientResponseError as error:
			if error.status == 401: self.authorized = False
			self.errors += 1
			log.error(f"{self.session_name} | Daily quests http error: {error.message}" + (f"\nTraceback: {traceback.format_exc()}" if config.DEBUG_MODE else ""))
			await asyncio.sleep(delay=3)
		except Exception as error:
			log.error(f"{self.session_name} | Daily quests error: {str(error)}" + (f"\nTraceback: {traceback.format_exc()}" if config.DEBUG_MODE else ""))
	
	async def complete_quest(self, quest: str, code:str) -> bool:
		url = self.api_url + '/quests/check'
		try:
			json_data = {'data': [quest, code]}
			await self.set_sign_headers(data=json_data)
			response = await self.http_client.post(url, json=json_data)
			response.raise_for_status()
			response_text = await response.text()
			if config.DEBUG_MODE:
				log.debug(f"{self.session_name} | Check quest response:\n{response_text}")
			response_json = json.loads(response_text)
			if response_json.get('success', False) and response_json['data'].get('result', False):
				await asyncio.sleep(delay=2)
				if await self.quest_reward(quest=quest, code=code):
					return True
			return False
		except aiohttp.ClientResponseError as error:
			if error.status == 401: self.authorized = False
			self.errors += 1
			log.error(f"{self.session_name} | Complete quest http error: {error.message}" + (f"\nTraceback: {traceback.format_exc()}" if config.DEBUG_MODE else ""))
			await asyncio.sleep(delay=3)
			return False
		except Exception as error:
			log.error(f"{self.session_name} | Complete quest error: {str(error)}" + (f"\nTraceback: {traceback.format_exc()}" if config.DEBUG_MODE else ""))
			return False
	
	async def friend_reward(self, friend: int) -> bool:
		url = self.api_url + '/friends/claim'
		try:
			json_data = {'data': friend}
			await self.set_sign_headers(data=json_data)
			response = await self.http_client.post(url, json=json_data)
			response.raise_for_status()
			response_text = await response.text()
			if config.DEBUG_MODE:
				log.debug(f"{self.session_name} | Friend reward response:\n{response_text}")
			response_json = json.loads(response_text)
			success = response_json.get('success', False)
			if success:
				self.errors = 0
				self.update_level(level=int(response_json['data']['hero']['level']))
				self.balance = int(response_json['data']['hero']['money'])
				self.mph = int(response_json['data']['hero']['moneyPerHour'])
				return True
			else: return False
		except aiohttp.ClientResponseError as error:
			if error.status == 401: self.authorized = False
			self.errors += 1
			log.error(f"{self.session_name} | Friend reward http error: {error.message}" + (f"\nTraceback: {traceback.format_exc()}" if config.DEBUG_MODE else ""))
			await asyncio.sleep(delay=3)
			return False
		except Exception as error:
			log.error(f"{self.session_name} | Friend reward error: {str(error)}" + (f"\nTraceback: {traceback.format_exc()}" if config.DEBUG_MODE else ""))
			return False
	
	def get_tap_limit(self) -> int:
		for level_info in self.dbData['dbLevels']:
			if level_info['level'] == self.level:
				return int(level_info['tapLimit'] or 0)
		return 0

	async def perform_taps(self, per_tap: int, energy: int, bonus_chance: float, bonus_mult: float) -> None:
		url = self.api_url + '/hero/action/tap'
		log.info(f"{self.session_name} | Taps started | moneyPerTap: {per_tap} | bonusChance: {bonus_chance:.2f} | bonusMultiplier: {bonus_mult:.2f}")
		tapped_today = 0
		tap_limit = self.get_tap_limit()
		taps_over = False
		last = False
		while not last:
			taps_per_second = random.randint(*config.TAPS_PER_SECOND)
			seconds = random.randint(4, 6)
			taps_sum = taps_per_second * seconds
			earned_money = 0
			for i in range(1, taps_sum + 1):
				tap_power = calculate_tap_power(per_tap, energy, bonus_chance, bonus_mult)
				earned_money += tap_power
				energy -= 0.7 * tap_power # cheat
			if energy < per_tap: last = True
			await asyncio.sleep(delay=seconds)
			try:
				json_data = {'data': {'data':{'task': {'amount': earned_money, 'currentEnergy': energy}}, 'seconds': seconds}}
				await self.set_sign_headers(data=json_data)
				response = await self.http_client.post(url, json=json_data)
				response.raise_for_status()
				response_text = await response.text()
				if config.DEBUG_MODE:
					log.debug(f"{self.session_name} | Taps response:\n{response_text}")
				response_json = json.loads(response_text)
				success = response_json.get('success', False)
				error = response_json.get('error', '')
				if success:
					self.errors = 0
					self.update_level(level=int(response_json['data']['hero']['level']))
					self.balance = int(response_json['data']['hero']['money'])
					self.mph = int(response_json['data']['hero']['moneyPerHour'])
					energy = int(response_json['data']['hero']['earns']['task']['energy'])
					tapped_today = int(response_json['data']['tapped_today'])
					log.success(f"{self.session_name} | Earned money: +{number_short(value=earned_money)} | Energy left: {number_short(value=energy)}")
					if tapped_today >= tap_limit: taps_over = True
					if last and not taps_over:
						log.warning(f"{self.session_name} | Taps stopped (not enough energy)")
				elif 'too many taps' in error: taps_over = True
				
				if taps_over:
					log.warning(f"{self.session_name} | Taps stopped (tap limit reached)")
					self.taps_limit = True
					cur_time_gmt = datetime.now(self.gmt_timezone)
					self.taps_limit_date = cur_time_gmt.strftime('%Y-%m-%d')
					last = True
			except aiohttp.ClientResponseError as error:
				if error.status == 401: self.authorized = False
				self.errors += 1
				log.error(f"{self.session_name} | Taps http error: {error.message}" + (f"\nTraceback: {traceback.format_exc()}" if config.DEBUG_MODE else ""))
				await asyncio.sleep(delay=3)
				break
			except Exception as error:
				log.error(f"{self.session_name} | Taps error: {str(error)}" + (f"\nTraceback: {traceback.format_exc()}" if config.DEBUG_MODE else ""))
				break

	async def perform_pvp(self, league: dict, strategy: str, count: int) -> None:
		url_info = self.api_url + '/pvp/info'
		url_fight = self.api_url + '/pvp/fight'
		url_cancel = self.api_url + '/pvp/fight/cancel'
		url_claim = self.api_url + '/pvp/claim'
		log.info(f"{self.session_name} | PvP negotiations started | League: {league['key']} | Strategy: {strategy}")
		json_data = {}
		await self.set_sign_headers(data=json_data)
		await self.http_client.post(url_info, json=json_data)
		await asyncio.sleep(3)
		curent_strategy = strategy
		money = 0
		search_attempts = 0
		while count > 0:
			if self.balance < int(league['maxContract']):
				money_str = f"Profit: +{number_short(value=money)}" if money > 0 else (f"Loss: {number_short(value=money)}" if money < 0 else "Profit: 0")
				log.warning(f"{self.session_name} | PvP negotiations stopped (not enough money). {money_str}")
				break
			if self.balance - int(league['maxContract']) < config.PROTECTED_BALANCE:
				money_str = f"Profit: +{number_short(value=money)}" if money > 0 else (f"Loss: {number_short(value=money)}" if money < 0 else "Profit: 0")
				log.warning(f"{self.session_name} | PvP negotiations stopped (balance protection). {money_str}")
				break
			
			if strategy == 'random': curent_strategy = random.choice(self.strategies)
			log.info(f"{self.session_name} | Searching opponent...")
			try:
				search_attempts += 1
				json_data = {'data': {'league': league['key'], 'strategy': curent_strategy}}
				await self.set_sign_headers(data=json_data)
				response = await self.http_client.post(url_fight, json=json_data)
				response.raise_for_status()
				response_text = await response.text()
				if config.DEBUG_MODE:
					log.debug(f"{self.session_name} | PvP search response:\n{response_text}")
				response_json = json.loads(response_text)
				success = response_json.get('success', False)
				if success:
					self.errors = 0
					if response_json['data']['opponent'] is None:
						if search_attempts > 2:
							json_data = {}
							await self.set_sign_headers(data=json_data)
							await self.http_client.post(url_cancel, json=json_data)
							search_attempts = 0
							log.info(f"{self.session_name} | Search cancelled")
						await asyncio.sleep(random.randint(5, 10))
						continue
					
					await asyncio.sleep(random.randint(6, 7))
					count -= 1
					search_attempts = 0
					if int(response_json['data']['fight']['player1']) == self.user_id:
						opponent_strategy = response_json['data']['fight']['player2Strategy']
					else:
						opponent_strategy = response_json['data']['fight']['player1Strategy']
					money_contract = response_json['data']['fight']['moneyContract']
					money_profit = response_json['data']['fight']['moneyProfit']
					winner = int(response_json['data']['fight']['winner'])
					if winner == self.user_id:
						money += money_profit
						log.success(f"{self.session_name} | Contract sum: {number_short(value=money_contract)} | "
									f"Your strategy: {curent_strategy} | "
									f"Opponent strategy: {opponent_strategy} | "
									f"You WIN (+{number_short(value=money_profit)})")
					else:
						money -= money_contract
						log.success(f"{self.session_name} | Contract sum: {number_short(value=money_contract)} | "
									f"Your strategy: {curent_strategy} | "
									f"Opponent strategy: {opponent_strategy} | "
									f"You LOSE (-{number_short(value=money_contract)})")
					
					json_data = {}
					await self.set_sign_headers(data=json_data)
					response = await self.http_client.post(url_claim, json=json_data)
					response.raise_for_status()
					response_text = await response.text()
					if config.DEBUG_MODE:
						log.debug(f"{self.session_name} | PvP claim response:\n{response_text}")
					response_json = json.loads(response_text)
					success = response_json.get('success', False)
					if success:
						self.errors = 0
						self.update_level(level=int(response_json['data']['hero']['level']))
						self.balance = int(response_json['data']['hero']['money'])
						self.mph = int(response_json['data']['hero']['moneyPerHour'])
					
					await asyncio.sleep(random.randint(1, 2))
			except aiohttp.ClientResponseError as error:
				if error.status == 401: self.authorized = False
				self.errors += 1
				log.error(f"{self.session_name} | PvP http error: {error.message}" + (f"\nTraceback: {traceback.format_exc()}" if config.DEBUG_MODE else ""))
				await asyncio.sleep(delay=3)
				break
			except Exception as error:
				log.error(f"{self.session_name} | PvP error: {str(error)}" + (f"\nTraceback: {traceback.format_exc()}" if config.DEBUG_MODE else ""))
				await asyncio.sleep(random.randint(10, 30))
				break
		money_str = f"Profit: +{number_short(value=money)}" if money > 0 else (f"Loss: {number_short(value=money)}" if money < 0 else "Profit: 0")
		log.info(f"{self.session_name} | PvP negotiations finished. {money_str}")

	async def get_helper(self) -> dict:
		url = 'https://alexell.pro/crypto/x-empire/data/'
		try:
			json_data = {'data': 'alexell'}
			await self.set_sign_headers(data=json_data)
			response = await self.http_client.post(url, json=json_data)
			if response.status in [200, 400, 401, 403]:
				response_json = await response.json()
				success = response_json.get('success', False)
				if success:
					return response_json.get('result', {})
				else:
					log.error(f"{self.session_name} | Get helper error: {response.status} {response_json.get('message', '')}")
					return {}
		except Exception as error:
			log.error(f"{self.session_name} | Get helper error: {str(error)}")
			return {}

	async def get_funds_info(self) -> dict:
		url = self.api_url + '/fund/info'
		try:
			json_data = {}
			await self.set_sign_headers(data=json_data)
			response = await self.http_client.post(url, json=json_data)
			response.raise_for_status()
			response_text = await response.text()
			if config.DEBUG_MODE:
				log.debug(f"{self.session_name} | Funds response:\n{response_text}")
			response_json = json.loads(response_text)
			return response_json['data']
		except aiohttp.ClientResponseError as error:
			if error.status == 401: self.authorized = False
			self.errors += 1
			log.error(f"{self.session_name} | Funds http error: {error.message}" + (f"\nTraceback: {traceback.format_exc()}" if config.DEBUG_MODE else ""))
			await asyncio.sleep(delay=3)
			return {}
		except Exception as error:
			log.error(f"{self.session_name} | Funds error: {error}" + (f"\nTraceback: {traceback.format_exc()}" if config.DEBUG_MODE else ""))
			await asyncio.sleep(delay=3)
			return {}

	async def invest(self, fund: str, amount: int) -> None:
		url = self.api_url + '/fund/invest'
		if self.balance < amount:
			log.warning(f"{self.session_name} | Not enough money for investing")
			return
		if self.balance - amount < config.PROTECTED_BALANCE:
			log.warning(f"{self.session_name} | Investing skipped (balance protection)")
			return
		try:
			json_data = {'data': {'fund': fund, 'money': amount}}
			await self.set_sign_headers(data=json_data)
			response = await self.http_client.post(url, json=json_data)
			response.raise_for_status()
			response_text = await response.text()
			if config.DEBUG_MODE:
				log.debug(f"{self.session_name} | Investing response:\n{response_text}")
			response_json = json.loads(response_text)
			success = response_json.get('success', False)
			if success:
				self.errors = 0
				self.update_level(level=int(response_json['data']['hero']['level']))
				self.balance = int(response_json['data']['hero']['money'])
				self.mph = int(response_json['data']['hero']['moneyPerHour'])
				for fnd in response_json['data']['funds']:
					if fnd['fundKey'] == fund:
						money = fnd['moneyProfit']
						money_str = f"Profit: +{number_short(value=money)}" if money > 0 else (f"Loss: {number_short(value=money)}" if money < 0 else "Profit: 0")
						log.success(f"{self.session_name} | Investing {number_short(value=amount)} in {fund} successfully. {money_str}")
						break
		except aiohttp.ClientResponseError as error:
			if error.status == 401: self.authorized = False
			self.errors += 1
			log.error(f"{self.session_name} | Investing http error: {error.message}" + (f"\nTraceback: {traceback.format_exc()}" if config.DEBUG_MODE else ""))
			await asyncio.sleep(delay=3)
		except Exception as error:
			log.error(f"{self.session_name} | Investing error: {str(error)}" + (f"\nTraceback: {traceback.format_exc()}" if config.DEBUG_MODE else ""))

	async def improve_skill(self, skill: str) -> dict | None:
		url = self.api_url + '/skills/improve'
		try:
			json_data = {'data': skill}
			await self.set_sign_headers(data=json_data)
			response = await self.http_client.post(url, json=json_data)
			response.raise_for_status()
			response_text = await response.text()
			if config.DEBUG_MODE:
				log.debug(f"{self.session_name} | Improve skill response:\n{response_text}")
			response_json = json.loads(response_text)
			success = response_json.get('success', False)
			if success:
				self.errors = 0
				self.update_level(level=int(response_json['data']['hero']['level']))
				self.balance = int(response_json['data']['hero']['money'])
				self.mph = int(response_json['data']['hero']['moneyPerHour'])
				return response_json['data']
			else: return None
		except aiohttp.ClientResponseError as error:
			if error.status == 401: self.authorized = False
			self.errors += 1
			log.error(f"{self.session_name} | Improve skill http error: {error.message}" + (f"\nTraceback: {traceback.format_exc()}" if config.DEBUG_MODE else ""))
			await asyncio.sleep(delay=3)
			return None
		except Exception as error:
			log.error(f"{self.session_name} | Improve skill error: {str(error)}" + (f"\nTraceback: {traceback.format_exc()}" if config.DEBUG_MODE else ""))
			return None

	def update_level(self, level: int) -> None:
		if self.level > 0 and level > self.level:
			log.success(f"{self.session_name} | You have reached a new level: {level}")
		self.level = level
	
	async def check_proxy(self, proxy: Proxy) -> None:
		try:
			response = await self.http_client.get(url='https://httpbin.org/ip', timeout=aiohttp.ClientTimeout(5))
			ip = (await response.json()).get('origin')
			log.info(f"{self.session_name} | Proxy IP: {ip}")
		except Exception as error:
			log.error(f"{self.session_name} | Proxy: {proxy} | Error: {error}")

	async def run(self, proxy: str | None) -> None:
		proxy_conn = ProxyConnector().from_url(proxy) if proxy else None

		async with aiohttp.ClientSession(headers=headers, connector=proxy_conn) as http_client:
			self.http_client = http_client
			if proxy:
				await self.check_proxy(proxy=proxy)
			
			day_start = time(9, 0)
			day_end = time(23, 59)
			self.gmt_timezone = ZoneInfo('GMT')
			main_delay = 0
			sum_delay = 0
			sleep_time = 0
			main_actions = True
			self.level = 0
			self.authorized = False
			while True:
				if self.errors >= config.ERRORS_BEFORE_STOP:
					log.error(f"{self.session_name} | Bot stopped (too many errors)")
					break
				try:
					if not self.authorized:
						login_data = await self.get_tg_web_data(proxy=proxy)
						if await self.login(json_data=login_data):
							log.success(f"{self.session_name} | Login successful")
							self.authorized = True
							self.http_client.headers['Api-Key'] = self.api_key
							full_profile = await self.get_profile(full=True)
							self.dbData = full_profile.get('dbData', {})
							if self.dbData: del full_profile['dbData']
							if self.user_id is None: self.user_id = int(full_profile['profile']['id'] or 0)
							self.balance = int(full_profile['hero']['money'] or 0)
							self.update_level(level=int(full_profile['hero']['level'] or 0))
							self.mph = int(full_profile['hero']['moneyPerHour'] or 0)
							offline_bonus = int(full_profile['hero']['offlineBonus'] or 0)
							if offline_bonus > 0:
								await asyncio.sleep(random.randint(1, 2))
								if await self.get_offline_bonus():
									log.success(f"{self.session_name} | Offline bonus claimed: +{number_short(value=offline_bonus)}")
							else:
								log.info(f"{self.session_name} | Offline bonus not available")
						else: continue
					
					await asyncio.sleep(random.randint(2, 4))
					profile = await self.get_profile(full=False)
					self.update_level(level=int(profile['hero']['level'] or 0))
					self.balance = int(profile['hero']['money'] or 0)
					self.mph = int(profile['hero']['moneyPerHour'] or 0)
					log.info(f"{self.session_name} | Level: {self.level} | "
								f"Balance: {number_short(value=self.balance)} | "
								f"Profit per hour: +{number_short(value=self.mph)}")
					
					cur_time_gmt = datetime.now(self.gmt_timezone)
					cur_time_gmt_s = cur_time_gmt.strftime('%Y-%m-%d')
					new_day_gmt = cur_time_gmt.replace(hour=7, minute=0, second=0, microsecond=0)
					
					if main_actions:
						daily_rewards = full_profile['dailyRewards']
						daily_index = None
						for day, status in daily_rewards.items():
							if status == 'canTake':
								daily_index = day
								break
						if daily_index is not None:
							log.info(f"{self.session_name} | Daily reward available")
							await asyncio.sleep(random.randint(2, 4))
							daily_claimed = await self.daily_reward(index=daily_index)
							if daily_claimed:
								log.success(f"{self.session_name} | Daily reward claimed")
								self.errors = 0
						else:
							log.info(f"{self.session_name} | Daily reward not available")
						
						unrewarded_quests = [quest['key'] for quest in full_profile['quests'] if not quest['isRewarded']]
						if unrewarded_quests:
							log.info(f"{self.session_name} | Quest rewards available")
							await asyncio.sleep(random.randint(2, 4))
							for quest in unrewarded_quests:
								await asyncio.sleep(random.randint(1, 2))
								if await self.quest_reward(quest=quest):
									log.success(f"{self.session_name} | Reward for quest {quest} claimed")
						
						await asyncio.sleep(random.randint(2, 4))
						await self.daily_quests()
						
						unrewarded_friends = [int(friend['id']) for friend in full_profile['friends'] if friend['bonusToTake'] > 0]
						if unrewarded_friends:
							log.info(f"{self.session_name} | Reward for friends available")
							await asyncio.sleep(random.randint(2, 4))
							for friend in unrewarded_friends:
								await asyncio.sleep(random.randint(1, 2))
								if await self.friend_reward(friend=friend):
									log.success(f"{self.session_name} | Reward for friend {friend} claimed")
						
						if config.PVP_ENABLED:
							if self.dbData:
								league_data = None
								selected_league = None
								for league in self.dbData['dbNegotiationsLeague']:
									if config.PVP_LEAGUE == 'auto':
										if self.level >= league['requiredLevel'] and self.level <= league['maxLevel']:
											if league_data is None or league['requiredLevel'] < league_data['requiredLevel']:
												league_data = league
									else:
										if league['key'] == config.PVP_LEAGUE:
											selected_league = league
											if self.level >= league['requiredLevel'] and self.level <= league['maxLevel']:
												league_data = league
												break
								
								# if the current league is no longer available, select the next league
								if config.PVP_LEAGUE != 'auto' and league_data is None:
									if selected_league:
										if config.PVP_UPGRADE_LEAGUE:
											for league in self.dbData['dbNegotiationsLeague']:
												if league['requiredLevel'] > selected_league['requiredLevel'] and self.level >= league['requiredLevel']:
													league_data = league
													break
											log.info(f"{self.session_name} | Selected league is no longer available. New league: {league_data['key']}.")
										else:
											config.PVP_ENABLED = False
											log.warning(f"{self.session_name} | Selected league is no longer available. PvP negotiations disabled.")
									else:
										config.PVP_ENABLED = False
										log.warning(f"{self.session_name} | PVP_LEAGUE param is invalid. PvP negotiations disabled.")

								if league_data is not None:
									self.strategies = [strategy['key'] for strategy in self.dbData['dbNegotiationsStrategy']]
									if config.PVP_STRATEGY == 'random' or config.PVP_STRATEGY in self.strategies:
										await asyncio.sleep(random.randint(2, 4))
										await self.perform_pvp(league=league_data, strategy=config.PVP_STRATEGY, count=config.PVP_COUNT)
									else:
										config.PVP_ENABLED = False
										log.warning(f"{self.session_name} | PVP_STRATEGY param is invalid. PvP negotiations disabled.")
							else:
								log.warning(f"{self.session_name} | Database is missing. PvP negotiations will be skipped this time.")
						
						# Quests with fakeCheck (2 quests at a time to avoid attracting attention)
						quests_completed = 0
						for dbQuest in self.dbData['dbQuests']:
							if quests_completed >= 2: break
							if dbQuest['isArchived']: continue
							if dbQuest['checkType'] != 'fakeCheck': continue
							if not any(dbQuest['key'] in quest['key'] for quest in full_profile['quests']):
								if await self.quest_reward(quest=dbQuest['key']):
									quests_completed += 1
									log.success(f"{self.session_name} | Reward for quest {dbQuest['key']} claimed")
									await asyncio.sleep(random.randint(10, 20))
						
						# Daily quiz and rebus
						quiz_key = ''
						quiz_answer = ''
						quiz_req_level = 0
						rebus_key = ''
						rebus_answer = ''
						rebus_req_level = 0
						for quest in self.dbData['dbQuests']:
							if quest['isArchived']: continue
							date_start = datetime.strptime(quest['dateStart'], '%Y-%m-%d %H:%M:%S') if quest.get('dateStart') else None
							date_end = datetime.strptime(quest['dateEnd'], '%Y-%m-%d %H:%M:%S') if quest.get('dateEnd') else None
							if date_start: date_start = date_start.replace(tzinfo=self.gmt_timezone)
							if date_end: date_end = date_end.replace(tzinfo=self.gmt_timezone)
							if date_start and date_end and not (date_start <= cur_time_gmt <= date_end): continue
							if 'riddle' in quest['key']:
								quiz_key = quest['key']
								quiz_answer = quest['checkData']
								quiz_req_level = int(quest['requiredLevel'] or 0)
							if 'rebus' in quest['key']:
								rebus_key = quest['key']
								rebus_answer = quest['checkData']
								rebus_req_level = int(quest['requiredLevel']  or 0)
						
						need_quiz = bool(quiz_key and quiz_answer) and not any(quiz_key in quest['key'] for quest in full_profile['quests'])
						need_rebus = bool(rebus_key and rebus_answer) and not any(rebus_key in quest['key'] for quest in full_profile['quests'])
						
						if need_quiz:
							day_end = time(random.randint(22, 23), random.randint(0, 59))
							log.info(f"{self.session_name} | Today the night period will begin at {str(day_end)}")
							if self.level >= quiz_req_level:
								await asyncio.sleep(random.randint(2, 4))
								if await self.complete_quest(quest=quiz_key, code=quiz_answer):
									need_quiz = False
									log.success(f"{self.session_name} | Reward for daily quiz claimed")
						if need_rebus:
							day_start = time(random.randint(8, 9), random.randint(0, 59))
							log.info(f"{self.session_name} | Tomorrow the daytime period will begin at {str(day_start)}")
							if self.level >= rebus_req_level:
								await asyncio.sleep(random.randint(2, 4))
								if await self.complete_quest(quest=rebus_key, code=rebus_answer):
									need_rebus = False
									log.success(f"{self.session_name} | Reward for daily rebus claimed")
						
						# Investing with external data for combo
						helper = await self.get_helper()
						if cur_time_gmt >= new_day_gmt and cur_time_gmt_s in helper:
							helper = helper[cur_time_gmt_s]
							if 'funds' in helper:
								regular_funds = helper['funds'].get('regular', [])
								special_fund = helper['funds'].get('special', None)
								special_fund = special_fund if any(fund['key'] == special_fund for fund in self.dbData['dbFunds']) else None
								current_funds = await self.get_funds_info()
								await asyncio.sleep(random.randint(4, 8))
								
								if regular_funds and 'funds' in current_funds and not current_funds['funds']:
									funds_to_invest = [special_fund] if special_fund else []
									funds_to_invest += regular_funds[:2] if special_fund else regular_funds
									for fund in funds_to_invest:
										await self.invest(fund=fund, amount=calculate_bet(level=self.level, mph=self.mph, balance=self.balance))
										await asyncio.sleep(random.randint(2, 4))
						
						# improve mining skills (+1 level to each per cycle)
						if config.MINING_SKILLS_LEVEL > 0:
							my_skills = full_profile['skills']
							friends_count = int(full_profile['profile']['friends'] or 0)
							for skill in self.dbData['dbSkills']:
								if skill['category'] != 'mining': continue
								if skill['key'] in my_skills:
									if my_skills[skill['key']]['level'] >= config.MINING_SKILLS_LEVEL: continue
								possible_skill = improve_possible(skill, my_skills, self.level, self.balance, friends_count)
								if possible_skill is not None:
									if self.balance - possible_skill['price'] >= config.PROTECTED_BALANCE:
										await asyncio.sleep(random.randint(1, 2))
										improve_data = await self.improve_skill(skill=possible_skill['key'])
										if improve_data is not None:
											log.success(f"{self.session_name} | Mining skill {possible_skill['key']} improved to level {possible_skill['newlevel']}")
										else:
											break
						
						# improve profit skills
						if config.SKILLS_COUNT > 0:
							improved_skills = 0
							improve_data = None
							while improved_skills < config.SKILLS_COUNT:
								skill = calculate_best_skill(skills=self.dbData['dbSkills'], ignored_skills=config.IGNORED_SKILLS, profile=full_profile, level=self.level, balance=self.balance, improve=improve_data)
								if skill is None: break
								if self.balance - skill['price'] < config.PROTECTED_BALANCE:
									log.warning(f"{self.session_name} | Skill improvement stopped (balance protection)")
									break
								await asyncio.sleep(random.randint(2, 4))
								improve_data = await self.improve_skill(skill=skill['key'])
								if improve_data is None: break
								improved_skills += 1
								log.success(f"{self.session_name} | Skill {skill['key']} improved to level {skill['newlevel']}")
						
						await asyncio.sleep(random.randint(2, 4))
						profile = await self.get_profile(full=False)
						self.update_level(level=int(profile['hero']['level'] or 0))
						self.balance = int(profile['hero']['money'] or 0)
						self.mph = int(profile['hero']['moneyPerHour'] or 0)
						log.info(f"{self.session_name} | Level: {self.level} | "
									f"Balance: {number_short(value=self.balance)} | "
									f"Profit per hour: +{number_short(value=self.mph)}")
					
						main_actions = False
						sum_delay = 0
					
					if config.TAPS_ENABLED:
						per_tap = int(profile['hero']['earns']['task']['moneyPerTap'] or 0)
						max_energy = int(profile['hero']['earns']['task']['limit'] or 0)
						energy = int(profile['hero']['earns']['task']['energy'] or 0)
						energy_recovery = int(profile['hero']['earns']['task']['recoveryPerSecond'] or 1)
						bonus_chance = float(profile['hero']['earns']['task']['bonusChance'] or 0)
						bonus_mult = float(profile['hero']['earns']['task']['bonusMultiplier'] or 0)
						if energy == max_energy and not self.taps_limit:
							await asyncio.sleep(random.randint(2, 4))
							await self.perform_taps(per_tap=per_tap, energy=energy, bonus_chance=bonus_chance, bonus_mult=bonus_mult)
							await asyncio.sleep(random.randint(2, 4))
							profile = await self.get_profile(full=False)
							max_energy = int(profile['hero']['earns']['task']['limit'] or 0)
							energy = int(profile['hero']['earns']['task']['energy'] or 0)
							energy_recovery = int(profile['hero']['earns']['task']['recoveryPerSecond'] or 1)

						energy_recovery_time = (max_energy - energy) / energy_recovery
						
						# Reset taps limit
						if cur_time_gmt >= new_day_gmt and cur_time_gmt_s != self.taps_limit_date:
							self.taps_limit = False
							self.taps_limit_date = ''
					
					now = datetime.now().time()
					if day_start <= now <= day_end:
						log_end = '(daytime main delay)'
						main_delay = 3600 # 1 hour delay during daytime
						if config.TAPS_ENABLED and not self.taps_limit:
							log_end = '(waiting for energy recovery)'
							sleep_time = energy_recovery_time
							sum_delay += sleep_time
							if sum_delay > main_delay:
								main_actions = True
						else:
							sleep_time = main_delay
					else:
						log_end = '(night main delay)'
						main_delay = 10800 # 3 hours delay at night
						sleep_time = main_delay
						main_actions = True
						sum_delay = 0
					
					random_sleep = random.randint(120, 300) # randomize delay within 5 minutes
					sleep_time += random_sleep
					sum_delay += random_sleep
					
					hours, minutes = divmod(sleep_time, 3600)
					minutes //= 60
					big_sleep = random.randint(config.BIG_SLEEP[0], config.BIG_SLEEP[1])
					if big_sleep > 1800: self.authorized = False
					log.info(f"{self.session_name} | Sleep {big_sleep}s")
					await asyncio.sleep(big_sleep)
					
				except RuntimeError as error:
					raise error
				except Exception as error:
					log.error(f"{self.session_name} | Unknown error: {error}" + (f"\nTraceback: {traceback.format_exc()}" if config.DEBUG_MODE else ""))
					await asyncio.sleep(delay=3)

async def run_bot(tg_client: Client, proxy: str | None):
	try:
		await CryptoBot(tg_client=tg_client).run(proxy=proxy)
	except RuntimeError as error:
		log.error(f"{tg_client.name} | Session error: {str(error)}")