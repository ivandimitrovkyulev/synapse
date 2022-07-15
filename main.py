import requests
import decimal


api = "https://syn-api-dev.herokuapp.com/v1/estimate_bridge_output" \
      "?fromChain={chainIn}&toChain={chainOut}" \
      "&fromToken={tokenIn}&toToken={tokenOut}" \
      "&amountFrom={amountIn}"

amount = 1000
decimals = 6
amountIn = amount * (10 ** decimals)
tokenIn = tokenOut = "USDC"
chainIn = "ETH"
chainOut = "BOBA"

url = api.format(amountIn=amountIn, tokenIn=tokenIn, tokenOut=tokenOut, chainIn=chainIn, chainOut=chainOut)
message = requests.get(url).json()

print(f"{amount} swapped for {message['amountToReceive']}")
amountOut = int(message['amountToReceive']) / (10 ** decimals)
print(f"{amount} swapped for {amountOut}")
