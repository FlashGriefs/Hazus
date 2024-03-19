import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from modules import cprint


def get_proxies():
    with open("proxies.txt", 'r') as file:
        proxies = []
        for line in file:
            stripped_line = line.strip()
            if not stripped_line.startswith('#'):
                proxies.append(stripped_line)
        return proxies

def read_proxies():
    with open("proxies.txt", 'r') as file:
        proxies = [line.strip() for line in file.readlines()]
    return proxies

def validate_proxy(proxy):
    try:
        response = requests.get("https://discord.com/", proxies={"http": proxy, "https": proxy}, timeout=4)
        is_valid = response.status_code == 200
    except requests.RequestException:
        is_valid = False
    return proxy, is_valid

def validate_proxies():
    max_threads = int(input("Max Threads: "))
    print ("Validating Proxies...")
    proxies = read_proxies()
    valid_proxies = []

    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        future_to_proxy = {executor.submit(validate_proxy, proxy): proxy for proxy in proxies}
        for future in as_completed(future_to_proxy):
            proxy, is_valid = future.result()
            if is_valid:
                valid_proxies.append(proxy)
                cprint(f"Valid proxy found: {proxy}", 0)
            else:
                cprint(f"Invalid proxy removed: {proxy}", 2)

    with open("proxies.txt", 'w') as file:
        file.write("""# MAKE SURE ALL YOUR PROXIES ARE EITHER HTTP OR HTTPS
# PROXY FORMAT: (proxy ip):(proxy port)
# Example: 127.0.0.1:100\n""")
        for proxy in valid_proxies:
            file.write(proxy + '\n')
    cprint("Validated Proxies.", 0)