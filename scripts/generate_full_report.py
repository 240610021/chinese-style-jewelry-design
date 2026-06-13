import json
from collections import Counter

with open(r'g:\Downloads\蔡规划\琢匠产品\parsed_products.json', 'r', encoding='utf-8') as f:
    products = json.load(f)

total = len(products)
with_sales = sum(1 for p in products if p['sales'])
with_price = sum(1 for p in products if p['price'])
with_reviews = sum(1 for p in products if p['reviews'])

sales_list = [p['sales'] for p in products if p['sales']]
price_list = [p['price'] for p in products if p['price']]
review_list = [p['reviews'] for p in products if p['reviews']]

cat_counter = Counter(p['category'] for p in products)

# Top sales
sorted_by_sales = sorted([p for p in products if p['sales']], key=lambda x: x['sales'], reverse=True)

report = []
report.append("=" * 70)
report.append("琢匠店铺 全量样本分析报告")
report.append("=" * 70)
report.append(f"样本总数: {total} 款")
report.append(f"成功提取价格: {with_price} 款 ({with_price/total*100:.1f}%)")
report.append(f"成功提取销量: {with_sales} 款 ({with_sales/total*100:.1f}%)")
report.append(f"成功提取评价: {with_reviews} 款 ({with_reviews/total*100:.1f}%)")
report.append("")

if price_list:
    report.append(f"价格统计 ({len(price_list)}款):")
    report.append(f"  最低: ¥{min(price_list):.2f}")
    report.append(f"  最高: ¥{max(price_list):.2f}")
    report.append(f"  平均: ¥{sum(price_list)/len(price_list):.2f}")
    report.append("")

if sales_list:
    report.append(f"销量统计 ({len(sales_list)}款):")
    report.append(f"  总销量: {sum(sales_list)} 件")
    report.append(f"  平均: {sum(sales_list)//len(sales_list)} 件/款")
    report.append(f"  最高: {max(sales_list)} 件")
    report.append(f"  最低: {min(sales_list)} 件")
    report.append("")

if review_list:
    report.append(f"评价统计 ({len(review_list)}款):")
    report.append(f"  总评价: {sum(review_list)} 条")
    report.append(f"  平均: {sum(review_list)//len(review_list)} 条/款")
    report.append("")

report.append("品类分布:")
for cat, cnt in cat_counter.most_common():
    report.append(f"  {cat}: {cnt} 款 ({cnt/total*100:.1f}%)")
report.append("")

report.append("=" * 70)
report.append("销量 TOP 20 爆款")
report.append("=" * 70)
for i, p in enumerate(sorted_by_sales[:20], 1):
    report.append(f"{i}. {p['title'][:60]}...")
    report.append(f"   品类: {p['category']} | 销量: {p['sales']} 件")
    report.append("")

report.append("=" * 70)
report.append("长尾/低销量商品 (销量<=50)")
report.append("=" * 70)
low_sales = [p for p in products if p['sales'] and p['sales'] <= 50]
for p in low_sales:
    report.append(f"- {p['title'][:60]}... | 品类: {p['category']} | 销量: {p['sales']} 件")

report_text = "\n".join(report)
print(report_text)

with open(r'g:\Downloads\蔡规划\琢匠产品\full_report.txt', 'w', encoding='utf-8') as f:
    f.write(report_text)

print(f"\n报告已保存到 g:\\Downloads\\蔡规划\\琢匠产品\\full_report.txt")
