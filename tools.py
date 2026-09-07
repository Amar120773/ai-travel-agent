import json
from logger import logger

def search_destinations(climate: str = None, budget: str = None) -> str:
    """Search for travel destinations based on climate and budget."""
    logger.info(f"Executing search_destinations with climate={climate}, budget={budget}")
    
    # Mock database
    destinations = [
        {"name": "Tokyo, Japan", "climate": "temperate", "budget": "high"},
        {"name": "Bali, Indonesia", "climate": "tropical", "budget": "medium"},
        {"name": "Reykjavik, Iceland", "climate": "cold", "budget": "high"},
        {"name": "Chiang Mai, Thailand", "climate": "tropical", "budget": "low"},
        {"name": "Cancun, Mexico", "climate": "tropical", "budget": "medium"},
    ]
    
    results = []
    for dest in destinations:
        match = True
        if climate and dest["climate"] != climate.lower():
            match = False
        if budget and dest["budget"] != budget.lower():
            match = False
        if match:
            results.append(dest)
            
    if not results:
        logger.debug("No destinations found matching criteria.")
        return json.dumps({"message": "No destinations found matching criteria."})
    
    logger.debug(f"Found {len(results)} matching destinations.")
    return json.dumps(results)

def get_flight_estimate(origin: str, destination: str) -> str:
    """Get an estimated flight cost and duration between two cities."""
    logger.info(f"Executing get_flight_estimate from {origin} to {destination}")
    # Mock data
    result = {
        "origin": origin,
        "destination": destination,
        "estimated_cost_usd": 650,
        "estimated_duration_hours": 8.5
    }
    return json.dumps(result)
