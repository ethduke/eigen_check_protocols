import json
import random
import brotli
from functools import wraps
import asyncio
import aiohttp
from tqdm import tqdm
from aiohttp import ClientSession
from config import APIConfig
from check_proxies import ProxyChecker

def retry_on_error(max_retries=5):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    response = await func(*args, **kwargs)
                    if response is None:
                        print(f"Received None response, retrying... (Attempt {attempt + 1})")
                        await asyncio.sleep(2)
                        continue
                    if isinstance(response, aiohttp.ClientResponse):
                        if response.status == 403:
                            print(f"403 Forbidden error encountered. Retrying... (Attempt {attempt + 1})")
                            await asyncio.sleep(2)
                            continue
                        content_type = response.headers.get('Content-Type', '')
                        if 'application/json' in content_type:
                            if response.headers.get('Content-Encoding') == 'br':
                                decompressed = brotli.decompress(await response.read())
                                return json.loads(decompressed.decode('utf-8'))
                            else:
                                return await response.json()
                        else:
                            text = await response.text()
                            print(f"Unexpected content type: {content_type}")
                            print(f"Response text: {text[:200]}...")
                            return []
                    else:
                        return response
                except Exception as e:
                    if attempt == max_retries - 1:
                        return []
                    await asyncio.sleep(2)
            return []
        return wrapper
    return decorator

@retry_on_error()
async def fetch_puffer_claims(session, address, proxy=None):
    url = f"{APIConfig.PUFFER['url']}{address}"
    async with session.get(url, proxy=proxy, timeout=aiohttp.ClientTimeout(total=10), headers=APIConfig.PUFFER['headers']) as response:
        return await response.json()

@retry_on_error()
async def fetch_etherfi_claims(session, address=None, proxy=None):
    url = f"{APIConfig.ETHERFI['url']}?address={address}"
    async with session.get(url, proxy=proxy,headers=APIConfig.ETHERFI['headers'], timeout=10) as response:
        return await response.json()

@retry_on_error()
async def fetch_eigen_s2_claims(session, address, proxy=None):
    url = f"{APIConfig.EIGEN_S2['url']}?walletAddress={address}"
    async with session.get(url, proxy=proxy, headers=APIConfig.EIGEN_S2['headers'], timeout=10) as response:
        return await response.json()

@retry_on_error()
async def fetch_renzo_claims(session, address, proxy=None):
    url = APIConfig.RENZO['url'].format(address=address)
    async with session.get(url, proxy=proxy, headers=APIConfig.RENZO['headers'], timeout=10) as response:
        return await response.json()

async def process_address(address, combined_data, apis_to_use):
    result = {"address": address}
    
    try:
        api_processors = {
            "PUFFER": lambda: (
                round(float(combined_data.get("puffer", [{}])[0].get("amount", 0)) * 1e-18, 3)
                if combined_data.get("puffer") and isinstance(combined_data["puffer"], list) else 0
            ),
            "ETHERFI": lambda: (
                round(float(combined_data.get("etherfi", {}).get("amount", 0)) * 1e-18, 3)
                if combined_data.get("etherfi") and isinstance(combined_data["etherfi"], dict) else 0
            ),
            "EIGEN_S2": lambda: (
                combined_data.get("eigen_s2", {}).get("season2", {}).get("data", {}).get("pipelines", {}).get("tokenQualified", 0)
                if isinstance(combined_data.get("eigen_s2"), dict) else 0
            ),
            "RENZO": lambda: (
                round(float(combined_data.get("renzo", [{}])[0].get("awardAmount", 0)) * 1e-18, 3)
                if combined_data.get("renzo") and isinstance(combined_data["renzo"], list) else 0
            )
        }

        for api in apis_to_use:
            if api in api_processors:
                value = api_processors[api]()
                if value > 0:
                    result[api.lower()] = value

    except Exception as e:
        print(f"Error processing address {address}: {str(e)}")
        print(f"Combined data: {combined_data}")
        return None
    
    return result if len(result) > 1 else None

async def process_addresses(fetch_func, addresses, working_proxies, desc):
    async with aiohttp.ClientSession(trust_env=True) as session:
        tasks = []
        results = {}

                # Step 1: Create tasks
        for address in addresses:
            proxy = random.choice(working_proxies) if working_proxies else None
            task = asyncio.create_task(fetch_func(session, address, proxy), name=address)
            task.address = address  # Attach address as an attribute to the task
            tasks.append(task)

        # Step 2: Process tasks as they complete
        for future in tqdm(
            asyncio.as_completed(tasks),
            total=len(tasks),
            desc=desc,
            unit="address"
        ):
            try:
                result = await future
                # Find the original task object
                original_task = next((task for task in tasks if task.done() and task.result() == result), None)
                
                if original_task:
                    address = original_task.address
                else:
                    address = "Unknown Address"
                
                results[address] = result
                #print(f"Completed task for address: {address} with result: {result}")
            except Exception as e:
                print(f"Error processing task: {e}")
                print(f"Task result: {result}")
                address = "Unknown Address"
                results[address] = None

        return results


async def process_puffer_addresses(addresses, working_proxies):
    return await process_addresses(fetch_puffer_claims, addresses, working_proxies, "Fetching Puffer data")

async def process_etherfi_addresses(addresses, working_proxies):
    return await process_addresses(fetch_etherfi_claims, addresses, working_proxies, "Fetching EtherFi data")

async def process_eigen_s2_addresses(addresses, working_proxies):
    return await process_addresses(fetch_eigen_s2_claims, addresses, working_proxies, "Fetching EIGEN_S2 data")

async def process_renzo_addresses(addresses, working_proxies):
    return await process_addresses(fetch_renzo_claims, addresses, working_proxies, "Fetching RENZO data")

async def main():

    # Choose which APIs to use
    apis_to_use = ["PUFFER", "EIGEN_S2", "RENZO", "ETHERFI"]


    print("Checking proxies...")
    working_proxies = await ProxyChecker().get_working_proxies()
    print(f"Found {len(working_proxies)} working proxies")

    if not working_proxies:
        print("No working proxies found. Continuing without proxies.")

    with open("evm.txt", "r") as file:
        addresses = [line.strip() for line in file]

    result_array = []
    puffer_results = await process_puffer_addresses(addresses, working_proxies)
    await asyncio.sleep(30)
    etherfi_results = await process_etherfi_addresses(addresses, working_proxies)
    await asyncio.sleep(30)
    eigen_s2_results = await process_eigen_s2_addresses(addresses, working_proxies)
    await asyncio.sleep(30)
    renzo_results = await process_renzo_addresses(addresses, working_proxies)

    
    for address in addresses:
        combined_data = {
            "puffer": puffer_results.get(address),
            "etherfi": etherfi_results.get(address),
            "eigen_s2": eigen_s2_results.get(address),
            "renzo": renzo_results.get(address)
        }
        
        processed_data = await process_address(address, combined_data, apis_to_use)
        if processed_data:
            result_array.append(processed_data)

    # Save result_array to JSON file
    with open('results.json', 'w') as json_file:
        json.dump(result_array, json_file, indent=4)
    
    print(f"Results saved to results.json")

    print("\nResults:")
    for result in result_array:
        print(f"\nAddress: {result['address']}")
        if 'puffer' in result:
            print(f"  PUFFER: {result['puffer']:.3f} EIGEN")
        if 'etherfi' in result:
            print(f"  ETHERFI: {result['etherfi']:.3f} EIGEN")
        if 'eigen_s2' in result:
            print(f"  EIGEN_S2: {result['eigen_s2']} EIGEN")
        if 'renzo' in result:
            print(f"  RENZO: {result['renzo']:.3f} EIGEN")
    
    total_wallets = len(result_array)
    total_eigen = sum(result.get('puffer', 0) + result.get('etherfi', 0) + result.get('eigen_s2', 0) + result.get('renzo', 0) for result in result_array)
    print(f"\nTotal number of wallets: {total_wallets}\nSum of Eigen found: {total_eigen:.3f}")

if __name__ == "__main__":
    asyncio.run(main())