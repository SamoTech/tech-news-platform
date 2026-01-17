from rss_fetch import fetch_all
from cleaner import clean_items

raw_items = fetch_all()
clean_items_list = clean_items(raw_items)

print("Raw items:", len(raw_items))
print("Clean items:", len(clean_items_list))

for item in clean_items_list[:5]:
    print("-" * 40)
    print(item["title"])
    print(item["source"], "|", item["category"])
    print(item["link"])
