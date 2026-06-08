# import requests
# import json

# response = requests.post(
#     "http://127.0.0.1:8000/scenario/simulate",
#     json={"query": "Reduce DTC demand by 15%"}
# )

# print("Status:", response.status_code)
# data = response.json()
# print("Summary:", data["summary"])
# print("Perturbations:", data["perturbations"])
# print("Forecast change:", data["adjusted_forecast"]["total_change_pct"])
# print("SKUs at risk:", data["stockout_risk"]["sku_count_at_risk"])
# print("Recommendations:", len(data["recommendations"]["recommendations"]))


import requests

queries = [
    "Reduce DTC demand by 15%",
    "What if we increase topline by 25%",
    "Apparel demand up 30%",
    "DTC down 15% while wholesale stays flat",
    "What happens if shipment delay 5 days",
]

for query in queries:
    response = requests.post(
        "http://127.0.0.1:8000/scenario/simulate",
        json={"query": query}
    )
    data = response.json()
    print(f"\nQuery: {query}")
    print(f"Perturbations: {data['perturbations']}")
    print(f"Forecast change: {data['adjusted_forecast']['total_change_pct']:.2f}%")
    print(f"Summary: {data['summary']}")
    print("-" * 60)