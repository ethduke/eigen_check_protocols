import fake_useragent

class APIConfig:
    user_agent = fake_useragent.UserAgent()
    headers =  {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en,en-US;q=0.9",
            "priority": "u=1, i",
            "sec-ch-ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "user-agent": user_agent.random
    }
    
    PUFFER = {
        "url": "https://api.hedgey.finance/token-claims/",
        "headers": {
            **headers,
            "origin": "https://claims.puffer.fi",
            "referer": "https://claims.puffer.fi/"
        }
    }
    SWELL = {
        "url": "https://v3-lrt.svc.swellnetwork.io/swell.v3.WalletService/EigenlayerAirdrop",
        "params": {
            "connect": "v1",
            "encoding": "json"
        },
        "headers": {
            **headers,
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-encoding": "gzip, deflate, br, zstd",
            "origin": "https://app.swellnetwork.io",
            "referer": "https://app.swellnetwork.io/dao/voyage/"
        }
    }
    ETHERFI = {
        "url": "https://claim.ether.fi/api/eigenlayer-claim-data",
        "headers": {
            **headers,
            "Referer": "https://claim.ether.fi/eigenlayer"
        }
    }
    EIGEN_S2 = {
        "url": "https://claims.eigenfoundation.org/clique-eigenlayer-api-v2/campaign/eigenlayer/credentials",
        "headers": {
            **headers,
            "Referer": "https://claims.eigenfoundation.org/",
            "Origin": "https://claims.eigenfoundation.org"
        }
    }
    RENZO = {
        "url": "https://airdrop-data-ezeigen.s3.us-west-2.amazonaws.com/{address}/0x6910c6df496dcb1fb2e2983ca69bb6fe62a7ade8d6289d9ad91d493d05a40aea-{address}.json",
        "headers": {
             **headers,
            "referer": "https://ezeigen.liquifi.finance/",
        }
    }
