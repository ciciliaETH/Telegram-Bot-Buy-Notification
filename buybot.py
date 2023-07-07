import requests
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters

last_transaction_id = None


def start(update, context):
    message = """🤖 Welcome to [@memesbuy_bot](https://t.me/MemesBuy_Bot)
        Powered by [@camelabs](https://t.me/camelabs)

        Introduce our bot
        1. [Disclaimer](https://t.me/camelabs/2)
        2. [Tutorial](https://t.me/camelabs/3)
        3. [Project Trending](https://t.me/camelabs/8)
        4. [Customer service](https://t.me/camelabs/5)
        5. [Fast track marketing](https://t.me/camelabs/5)"""

    context.bot.send_message(
        chat_id=update.effective_chat.id, text=message, parse_mode='Markdown')


def add(update: Update, context):
    keyboard = [
        [InlineKeyboardButton("Binance Smart Chain", callback_data='bsc')],
        [InlineKeyboardButton("Ethereum", callback_data='eth')],
        [InlineKeyboardButton("Polygon", callback_data='polygon')],
        [InlineKeyboardButton("Arbitrum", callback_data='arbitrum')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Please select a network:", reply_markup=reply_markup)


def button_callback(update: Update, context):
    query = update.callback_query
    network = query.data

    if network == 'bsc':
        message = "Halo! Ready to provide buying and selling information on Binance Smart Chain. Please enter the token address."
        context.bot.send_message(chat_id=query.message.chat_id, text=message)
    elif network in ['eth', 'polygon', 'arbitrum']:
        message = "COMING SOON"
        context.bot.send_message(chat_id=query.message.chat_id, text=message)


def format_number(number):
    if number >= 1e12:
        return f"{number/1e12:.2f} Triliun"
    elif number >= 1e9:
        return f"{number/1e9:.2f} Miliar"
    elif number >= 1e6:
        return f"{number/1e6:.2f} Juta"
    else:
        return str(number)


def handle_message(update: Update, context):
    token_address = update.message.text
    tx_api_url = f"https://api.bscscan.com/api?module=account&action=tokentx&address={token_address}&startblock=0&endblock=999999999&sort=desc&apikey=TDZX2A282D1SFWGSWECYGCU8U9ZP1XCMCE"

    try:
        global last_transaction_id
        while True:
            tx_response = requests.get(tx_api_url)
            tx_data = tx_response.json()

            if tx_data["status"] == "1" and "result" in tx_data:
                transactions = tx_data["result"]

                if len(transactions) > 0:
                    latest_transaction = transactions[0]
                    transaction_id = latest_transaction["hash"]

                    if transaction_id != last_transaction_id:
                        last_transaction_id = transaction_id

                        from_address = latest_transaction["from"]
                        to_address = latest_transaction["to"]
                        amount = latest_transaction["value"]
                        token_symbol = latest_transaction["tokenSymbol"]

                        # Gecko Terminal API
                        gecko_url = f"https://app.geckoterminal.com/api/p1/bsc/pools/{token_address}/swaps?include=from_token%2Cto_token&pair_id=1746877&page=1"
                        gecko_response = requests.get(gecko_url)
                        gecko_data = gecko_response.json()
                        latest_swap = gecko_data["data"][0]

                        timestamp = latest_swap["attributes"]["timestamp"]
                        tx_hash = latest_swap["attributes"]["tx_hash"]
                        tx_from_address = latest_swap["attributes"]["tx_from_address"]
                        from_token_amount = latest_swap["attributes"]["from_token_amount"]
                        price_from_in_usd = latest_swap["attributes"]["price_from_in_usd"]
                        to_token_amount = latest_swap["attributes"]["to_token_amount"]
                        price_to_in_currency_token = str(
                            round(float(latest_swap['attributes']['price_to_in_currency_token']), 4))
                        price_to_in_usd = str(
                            round(float(latest_swap['attributes']['price_to_in_usd']), 4))

                        # Gecko Terminal API
                        gecko_terminal_url = f"https://api.geckoterminal.com/api/v2/networks/bsc/pools/{token_address}"
                        gecko_terminal_response = requests.get(
                            gecko_terminal_url)
                        gecko_terminal_data = gecko_terminal_response.json()
                        fdv_usd = float(
                            gecko_terminal_data['data']['attributes']['fdv_usd'])
                        formatted_fdv_usd = format_number(fdv_usd)
                        price_change_percentage = gecko_terminal_data['data'][
                            'attributes']['price_change_percentage']['h24']

                        message = f"{token_symbol} Buy!\n🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢\n\n💵{price_to_in_currency_token}BNB (${price_to_in_usd})\n🪙{to_token_amount} {latest_swap['relationships']['to_token']['data']['type']} {token_symbol}\n🔼{price_change_percentage}\n🔼Market Cap ${formatted_fdv_usd}"
                        context.bot.send_message(
                            chat_id=update.effective_chat.id, text=message)

                time.sleep(5)
            else:
                message = "No transactions found."
                context.bot.send_message(
                    chat_id=update.effective_chat.id, text=message)
                break

    except requests.exceptions.RequestException as e:
        message = "An error occurred while fetching data from the BscScan API."
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=message)


def main():
    updater = Updater(
        token="6235418924:AAEOVPmmH_fTzbKA4WAZt9aIcJkD3Xp0erg", use_context=True)
    dispatcher = updater.dispatcher

    start_handler = CommandHandler('start', start)
    add_handler = CommandHandler('add', add)
    button_handler = CallbackQueryHandler(button_callback)
    message_handler = MessageHandler(
        Filters.text & ~Filters.command, handle_message)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(add_handler)
    dispatcher.add_handler(button_handler)
    dispatcher.add_handler(message_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
