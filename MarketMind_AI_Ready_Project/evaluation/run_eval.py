from src.tools.registry import calculate_metric, search_information

def main():
    print("MarketMind deterministic smoke evaluation")
    assert round(calculate_metric("growth_rate",[100,125])["result"],3) == .25
    assert search_information("AI customer support")["hits"]
    print("PASS")

if __name__ == "__main__":
    main()
