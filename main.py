import csv
import json
import os
import time

from binance.spot import Spot
from dotenv import load_dotenv

load_dotenv()

MEMO = str(os.getenv("MEMO"))
ADRESS = str(os.getenv("ADRESS"))
API_KEY = str(os.getenv("API_KEY"))
SECRET_KEY = str(os.getenv("SECRET_KEY"))
COIN = str(os.getenv("COIN"))

client = Spot(api_key=API_KEY, api_secret=SECRET_KEY)


def check_balance(client: Spot, coin=COIN) -> float:
    balance = float(
        list(filter(lambda x: x["coin"] == coin, client.coin_info()))[0]["free"]
    )
    print(
        f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())}\tbalance: {balance:.4f}"
    )
    return balance


def check_deposit_history(client, filename="deposit_history.json", coin=COIN):
    data = client.deposit_history()
    json_data = json.dumps(data, indent=4, sort_keys=True)
    last_deposit_data = max(
        list(filter(lambda x: x["coin"] == coin, data)),
        key=lambda x: x["insertTime"],
    )
    deposit_time = time.strftime(
        "%Y-%m-%d %H:%M:%S", time.gmtime(int(str(last_deposit_data["insertTime"])[:-3]))
    )
    amount = float(last_deposit_data["amount"])
    txId = last_deposit_data["txId"]
    csv_data = {
        "type": "deposit",
        "amount": str(amount),
        "time": deposit_time,
        "txId": txId,
    }
    if (
        json_data + "\n" != open(filename, "r").read()
        and last_deposit_data["status"] == 1
        and check_csv(csv_data)
    ):
        print(json_data, file=open(filename, "w"))
        print(f"NEW DEPOSIT \tcoin: {coin}\tamount: {amount}\ttime: {deposit_time}")


def check_withdraw_history(client, filename="deposit_history.json", coin=COIN):
    pass


def check_csv(new_data: dict):
    with open("table.csv") as csv_file:
        old_data = list(csv.DictReader(csv_file))
        if new_data in old_data:
            return False
    data = old_data + [new_data]
    with open("table.csv", "w") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=("type", "amount", "time", "txId"))
        writer.writeheader()
        writer.writerows(data)
        return True


# TODO:
# проверка баланса, потом проверка отличается ли данные в файле с тем что вернул запрос,
# проверка новых приходов (deposit_history) (убираются три нолика во времени) и уходов (withdraw_histoy),
# чекается статус последнего, вывод в консоль и сохранение в документ
# смотрим на applyTime и сумму
# потом возможно допилю запись даты в таблицу и построение графика

# а так впринципе если деньги есть то можно хуячить


# пока пендинг мб будет так что нельзя отправить, ща проверим

# можно в отдельном треде проверку истори сделать


# сначала проверка, пришли ли новые данные затем отправка данных в таблицу о новом приходе

print(
    json.dumps(client.withdraw_history(), indent=4, sort_keys=True),
    file=open("withdraw_history.json", "w"),
)


if __name__ == "__main__":
    while True:
        check_deposit_history(client)
        time.sleep(5)
        balance = float(f"{check_balance(client):.4f}")
        time.sleep(5)
        if balance > 1:
            client.withdraw(coin=COIN, amount=balance, address=ADRESS, addressTag=MEMO)
        time.sleep(5)
        check_withdraw_history(client)
        time.sleep(5)
