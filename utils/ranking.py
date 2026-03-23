def collapse_query_matches(raw_matches: list[dict]) -> list[dict]:
    grouped = {}
    for match in raw_matches:
        key = (match["relevant_url"], match["origin_url"], match["depth"])
        if key not in grouped:
            grouped[key] = {
                "relevant_url": match["relevant_url"],
                "origin_url": match["origin_url"],
                "depth": match["depth"],
                "total_frequency": 0
            }
        grouped[key]["total_frequency"] += match.get("frequency", 0)
    
    return list(grouped.values())

def sort_search_results(results: list[dict]) -> list[dict]:
    return sorted(
        results,
        key=lambda x: (-x["total_frequency"], x["depth"], x["relevant_url"])
    )
