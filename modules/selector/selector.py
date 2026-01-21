from collections import defaultdict
import random

TARGET_TOTAL = 45

CATEGORY_QUOTA = {
    "ai": 10,
    "smartphones": 10,
    "companies": 10,
    "gaming": 5,
    "general_tech": 10
}

def group_by_category(items):
    grouped = defaultdict(list)
    for item in items:
        grouped[item["category"]].append(item)
    return grouped

def weighted_shuffle(items):
    return sorted(items, key=lambda x: random.random() * (1 / item_weight(x)))

def item_weight(item):
    return item.get("weight", 1.0)

def select_news(items):
    grouped = group_by_category(items)
    selected = []

    for category, quota in CATEGORY_QUOTA.items():
        pool = grouped.get(category, [])
        if not pool:
            continue

        shuffled = weighted_shuffle(pool)
        selected.extend(shuffled[:quota])

    if len(selected) < TARGET_TOTAL:
        remaining = [i for i in items if i not in selected]
        remaining = weighted_shuffle(remaining)
        selected.extend(remaining[:TARGET_TOTAL - len(selected)])

    return selected[:TARGET_TOTAL]
