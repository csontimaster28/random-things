import json, os
MARKET_FILE = "data/market.json"

def load_market():
    if not os.path.exists(MARKET_FILE):
        return []
    with open(MARKET_FILE,"r") as f:
        return json.load(f)

def save_market(market):
    with open(MARKET_FILE,"w") as f:
        json.dump(market,f,indent=4)

def list_card(username, card, price):
    market = load_market()
    market.append({"owner":username,"card":card,"price":price,"bid":None})
    save_market(market)

def buy_card(buyer,index):
    from modules.user_system import spend_coins, add_coins
    market = load_market()
    if index>=len(market):
        return False,"Invalid index"
    item = market[index]
    if item["owner"]==buyer:
        return False,"Cannot buy your own card"
    price = item["price"]
    if spend_coins(buyer, price):
        add_coins(item["owner"], price)
        del market[index]
        save_market(market)
        return True,"Card purchased successfully!"
    return False,"Not enough coins"

def bid_card(bidder,index,amount):
    from modules.user_system import load_users, save_users
    users = load_users()
    market = load_market()
    if index>=len(market):
        return False,"Invalid index"
    item = market[index]
    if item["owner"]==bidder:
        return False,"Cannot bid on your own card"
    current_bid = item.get("bid",0)
    if amount<=current_bid:
        return False,"Bid must be higher than current bid"
    if users[bidder]["coins"]<amount:
        return False,"Not enough coins"
    # Refund previous bidder
    if item.get("bidder"):
        users[item["bidder"]]["coins"] += item["bid"]
    users[bidder]["coins"] -= amount
    save_users(users)
    item["bid"] = amount
    item["bidder"] = bidder
    save_market(market)
    return True,"Bid placed"
