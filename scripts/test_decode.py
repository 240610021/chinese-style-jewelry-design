import quopri
with open(r"g:\Downloads\蔡规划\新建文件夹\有龙则灵丨琢匠国风原创文玩手串配件龙头三通diy饰品隔珠链接扣-淘宝网.mhtml", 'r', encoding='utf-8', errors='ignore') as f:
    raw = f.read()

html_start = raw.find('<!DOCTYPE html>')
if html_start == -1:
    html_start = raw.find('<html')
html_raw = raw[html_start:]

# Decode quoted-printable
html = quopri.decodestring(html_raw.encode()).decode('utf-8', errors='ignore')
print(html[:500])
print('---')
print('Title contains 有龙则灵:', '有龙则灵' in html)
