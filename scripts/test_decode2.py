import quopri
import re
with open(r"g:\Downloads\蔡规划\新建文件夹\有龙则灵丨琢匠国风原创文玩手串配件龙头三通diy饰品隔珠链接扣-淘宝网.mhtml", 'r', encoding='utf-8', errors='ignore') as f:
    raw = f.read()

html_start = raw.find('<!DOCTYPE html>')
if html_start == -1:
    html_start = raw.find('<html')
html_raw = raw[html_start:]
html = quopri.decodestring(html_raw.encode()).decode('utf-8', errors='ignore')

# Check for price patterns
print('Price patterns:')
for m in re.finditer(r'¥\s*(\d+\.?\d*)', html):
    print(' ', m.group(0))

print('\nSales patterns:')
for m in re.finditer(r'(?:月销|已售|销量)[\s:：]*(\d+)', html):
    print(' ', m.group(0))

print('\nReview patterns:')
for m in re.finditer(r'(?:累计评论|评价)[\s:：]*(\d+)', html):
    print(' ', m.group(0))

print('\nShop patterns:')
for m in re.finditer(r'店铺[：:]\s*([^\n<]+)', html):
    print(' ', m.group(0))
