from fake_useragent import UserAgent

headers = {
	'Accept': '*/*',
	'Accept-Language': 'ru,ru-RU;q=0.9,en-US;q=0.8,en;q=0.7',
	'Content-Type' : 'application/json',
	'Is-Beta-Server' : 'null',
	'Origin': 'https://game.muskempire.io',
	'Referer': 'https://game.muskempire.io/',
	'Sec-Fetch-Dest': 'empty',
	'Sec-Fetch-Mode': 'cors',
	'Sec-Fetch-Site': 'same-site',
	'User-Agent': UserAgent(os='android').random,
	'Sec-Ch-Ua': '"Chromium";v="124", "Android WebView";v="124", "Not-A.Brand";v="99"',
	'Sec-Ch-Ua-Mobile': '?1',
	'Sec-Ch-Ua-Platform': '"Android"',
	'X-Requested-With' : 'org.telegram.messenger.web'
}
