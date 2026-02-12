import requests

def get_gold_silver():
    url = "https://metals-api.com/api/latest?access_key=DEMO&symbols=XAU,XAG"
    data = requests.get(url).json()
    gold = data["rates"]["XAU"]
    silver = data["rates"]["XAG"]
    return gold, silver

gold, silver = get_gold_silver()
print("Altın:", gold)
print("Gümüş:", silver)
