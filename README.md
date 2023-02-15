# Synapse v0.0.1

Program that screens https://synapseprotocol.com for arbitrage through their APIs.
<br>
Alerts via a Telegram message if something of interest is found.


## Installation ##

This project uses **Python 3.10** and **poetry 1.3.2**

Clone the project:
```
git clone https://github.com/ivandimitrovkyulev/synapse.git

cd synapse
```

Configure and activate virtual environment:

```
python config --local virtualenvs.in-project true

poetry shell
```

Install all third-party project dependencies:
```
poetry install
```

Create a Telegram Bot and save the following variables in a **.env** file in **./synapse**:
```
TOKEN=<telegram-token-for-your-bot>

CHAT_ID_ALERTS=<id-of-telegram-chat-for-alerts>

CHAT_ID_SPECIAL=<id-of-telegram-special-chat-for-alerts>

CHAT_ID_DEBUG=<id-of-telegram-chat-for-debugging>
```

## Running the script

To screen https://synapseprotocol.com for arbitrage:
```
python3 web.py "$(cat web.json)"
```

Where **input.json** are variables for screening:
```
{   
    "settings": {
        "sleep_time": 0, "max_wait_time": 15, "special_chat": {"max_swap_amount": 10000, "coins": ["USDC"]}
    },
    "coins": {
        "USDC": {
            "swap_amount": [10000, 100000],
            "networks": {
                "Optimism":  {"decimals": 6,  "chain_id": 10,         "token": "USDC", "arbitrage": 30},
                "Fantom":    {"decimals": 6,  "chain_id": 250,        "token": "USDC", "arbitrage": 30},
                "Arbitrum":  {"decimals": 6,  "chain_id": 42161,      "token": "USDC", "arbitrage": 30},
                "Avalanche": {"decimals": 6,  "chain_id": 43114,      "token": "USDC", "arbitrage": 30},
                "Binance":   {"decimals": 18, "chain_id": 56,         "token": "USDC", "arbitrage": 30},
                "Polygon":   {"decimals": 6,  "chain_id": 137,        "token": "USDC", "arbitrage": 30},
                "Aurora":    {"decimals": 6,  "chain_id": 1313161554, "token": "USDC", "arbitrage": 30},
                "Canto":     {"decimals": 6,  "chain_id": 7700,       "token": "USDC", "arbitrage": 30}
            }
        }
    }
}
```
<br>

All log filles are saved in **./logs**


## Docker Deploy ##

```
# To build a Docker image
docker build -f Dockerfile.web . -t synapse_web_image

# To run container
docker run --name="synapse_web" -it -d "synapse_web_image" python3 web.py "$(cat web.json)"
```

<br>
Contact: ivandkyulev@gmai.com