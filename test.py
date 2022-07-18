from src.synapse.api import get_bridge_output


arguments = [[10000, 310000, 10000], [6, 1, 'USDC'], [6, 10, 'USDC']]
a = get_bridge_output(*arguments)

print(f"Sell {a[1]:,} for {a[0]:,.3f} arbitrage")
