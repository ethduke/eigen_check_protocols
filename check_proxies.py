import asyncio
import random
import aiohttp

class ProxyChecker:
    def __init__(self):
        with open("proxies.txt", "r") as proxy_file:
            self.proxies = [line.strip() for line in proxy_file]
        self.working_proxies = []

    async def check_proxy(self, session, proxy):
        test_url = "http://httpbin.org/ip"
        try:
            async with session.get(test_url, proxy=proxy, timeout=5) as response:
                if response.status == 200:
                    return True
        except Exception:
            pass
        return False

    async def get_working_proxies(self):
        async with aiohttp.ClientSession() as session:
            tasks = [self.check_proxy(session, proxy) for proxy in self.proxies]
            results = await asyncio.gather(*tasks)
            self.working_proxies = [proxy for proxy, is_working in zip(self.proxies, results) if is_working]
            random.shuffle(self.working_proxies)
            return self.working_proxies

    def get_random_proxy(self):
        return random.choice(self.working_proxies or asyncio.run(self.get_working_proxies()))