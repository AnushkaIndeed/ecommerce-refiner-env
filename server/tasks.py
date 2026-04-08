# server/tasks.py
TASKS = {
    "easy": [
        {"input": "NIKE AIR MAX - RED - SIZE 10", "target": {"brand": "Nike", "color": "Red"}},
        {"input": "ADIDAS ULTRABOOST BLUE 42", "target": {"brand": "Adidas", "color": "Blue"}}
    ],
    "medium": [
        {"input": "Rugged Case for iPhone 15 - 6.1 inch", "target": {"brand": "Apple", "size_mm": 154.9}},
        {"input": "Gaming Monitor 27 inch Curved", "target": {"brand": "Unknown", "size_mm": 685.8}}
    ],
    "hard": [
        {"input": "Apple green silk dress by Zara", "target": {"brand": "Zara", "color": "Apple Green"}},
        {"input": "Puma Suede Classic - North Face Edition", "target": {"brand": "Puma", "collab": "The North Face"}}
    ]
}