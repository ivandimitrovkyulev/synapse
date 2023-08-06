Synapse v0.0.1
=======================================================================================================================
### version v1.1.0

-----------------------------------------------------------------------------------------------------------------------

Program that screens https://synapseprotocol.com for arbitrage through their APIs.
<br>
Alerts via a Telegram message if something of interest is found.


### Installation

This project uses **Python 3.11** and **poetry 1.5.1**

Clone the project:
```
git clone https://github.com/ivandimitrovkyulev/synapse.git

cd synapse
```

Configure and activate virtual environment:

```shell
python config --local virtualenvs.in-project true

poetry shell
```

Install all third-party project dependencies:
```shell
poetry install
```

Create a Telegram Bot and save the following variables in a **.env** file in **./synapse**:
```dotenv
TOKEN=<telegram-token-for-your-bot>

CHAT_ID_ALERTS=<id-of-telegram-chat-for-alerts>

CHAT_ID_SPECIAL=<id-of-telegram-special-chat-for-alerts>

CHAT_ID_DEBUG=<id-of-telegram-chat-for-debugging>
```


### Running the script

To screen https://synapseprotocol.com for arbitrage:
```shell
python3 web.py "$(cat web.json)"
```

Where **input.json** are variables for screening:
```json
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


### Docker

```shell
# To build a Docker image
docker build -f docker/web/Dockerfile . -t synapse_web

# Tag
docker tag synapse_web eu.gcr.io/project-id/synapse_web:latest

# Push to GCP
docker push synapse_web eu.gcr.io/project-id/synapse_web:latest

# To run container
docker run --name="synapse_web" -d -v $(pwd)/web.json:/app/web.json "synapse_web"
```

### Development
To update to lates version:
```shell
./update_version.py
```

<br>
Contact: ivandkyulev@gmai.com
