import requests


url = "https://syn-api-dev.herokuapp.com/v1/estimate_bridge_output" \
      "?fromChain={chainIn}&toChain={chainOut}" \
      "&fromToken={tokenIn}&toToken={tokenOut}" \
      "&amountFrom={amountIn}"

amount = 10
amountIn = amount * (10 ** 6)
tokenIn = tokenOut = "USDC"
chainIn = "ETH"
chainOut = "HARMONY"

http_req = url.format(amountIn=amountIn, tokenIn=tokenIn, tokenOut=tokenOut, chainIn=chainIn, chainOut=chainOut)
message = requests.get(http_req).json()

amountOut = int(message['amountToReceive']) / (10 ** 18)
print(f"{amount} swapped for {amountOut}")