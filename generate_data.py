import csv
import datetime
import random

def generate_sample_dataset(output_path):
    random.seed(42)
    
    categories = {
        "Electronics": [
            {"product": "Wireless Bluetooth Mouse", "price": 25.0},
            {"product": "Mechanical Keyboard", "price": 65.0},
            {"product": "USB-C Fast Charger", "price": 20.0},
            {"product": "Noise-Cancelling Headphones", "price": 120.0},
            {"product": "Smart Fitness Watch", "price": 85.0},
            {"product": "Portable External SSD 1TB", "price": 110.0}
        ],
        "Fashion": [
            {"product": "Cotton Crewneck T-Shirt", "price": 18.0},
            {"product": "Slim Fit Denim Jeans", "price": 45.0},
            {"product": "Casual Canvas Sneakers", "price": 55.0},
            {"product": "Classic Leather Belt", "price": 22.0}
        ],
        "Home & Kitchen": [
            {"product": "Stainless Steel Water Bottle", "price": 15.0},
            {"product": "Automatic Drip Coffee Maker", "price": 75.0},
            {"product": "Air Fryer 4L", "price": 95.0},
            {"product": "Non-Stick Frying Pan Set", "price": 40.0}
        ],
        "Groceries": [
            {"product": "Organic Roasted Coffee Beans", "price": 16.0},
            {"product": "Premium Extra Virgin Olive Oil", "price": 22.0},
            {"product": "Almonds & Cashews Trail Mix", "price": 14.0},
            {"product": "Organic Green Tea Box", "price": 12.0}
        ]
    }
    
    # 200 days of sales data
    start_date = datetime.date(2025, 1, 1)
    num_days = 200
    
    records = []
    
    for day_offset in range(num_days):
        current_date = start_date + datetime.timedelta(days=day_offset)
        date_str = current_date.strftime("%Y-%m-%d")
        day_of_week = current_date.weekday()  # 0=Mon, 5=Sat, 6=Sun
        
        # Weekend multiplier & upward growth trend over time
        weekend_mult = 1.35 if day_of_week in [5, 6] else 1.0
        trend_mult = 1.0 + (day_offset / num_days) * 0.4  # 40% growth over 200 days
        
        # Number of transactions on this day (1 to 3 items)
        daily_transactions = random.randint(1, 3)
        if day_of_week in [5, 6]:
            daily_transactions += random.randint(0, 1)
            
        for _ in range(daily_transactions):
            cat_name = random.choice(list(categories.keys()))
            item_info = random.choice(categories[cat_name])
            product_name = item_info["product"]
            base_price = item_info["price"]
            
            # Base quantity
            base_qty = random.randint(1, 4)
            # Adjust quantity by weekend and trend
            qty = max(1, int(round(base_qty * weekend_mult * (0.9 + random.random() * 0.3))))
            
            # Slight price variation / discount
            discount = random.choice([0.9, 0.95, 1.0, 1.0, 1.05])
            unit_price = round(base_price * discount, 2)
            
            # Total sales for this line item with small random noise
            sales = round(qty * unit_price * trend_mult * (0.95 + random.random() * 0.1), 2)
            
            records.append({
                "Date": date_str,
                "Product": product_name,
                "Category": cat_name,
                "Quantity": qty,
                "Unit_Price": unit_price,
                "Sales": sales
            })

    # Write to CSV
    with open(output_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Date", "Product", "Category", "Quantity", "Unit_Price", "Sales"])
        writer.writeheader()
        writer.writerows(records)

    print(f"Generated {len(records)} realistic sales records in {output_path}")

if __name__ == "__main__":
    import os
    os.makedirs("data", exist_ok=True)
    generate_sample_dataset("data/sample_sales.csv")
