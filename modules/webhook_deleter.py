import colorama
import requests
from modules import cprint
from modules import validate_webhook

def webhook_deleter():
    try:
        webhook = input(colorama.Fore.RESET + "Webhook to delete: ")

        if validate_webhook(webhook) is False:
            cprint("Invalid Webhook\n", 1)
            webhook_deleter()

        response = requests.delete(webhook)
        if response.status_code == 204:
            cprint("Webhook deleted successfully.\n", 0)
        else:
            cprint("Failed to delete webhook - if the issue persists dm me on discord: flashgriefs\n", 1)
            webhook_deleter()
    except KeyboardInterrupt:
        print ("")