from fake_useragent import UserAgent

headers = {
        'Accept': '*/*',
        'Accept-Language': 'ru,en;q=0.9,en-GB;q=0.8,en-US;q=0.7',
        'Connection': 'keep-alive',
        'Origin': 'https://botui.pocketfi.org',
        'Referer': 'https://botui.pocketfi.org/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': UserAgent(os='android').random,
        'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Android WebView";v="122"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
}