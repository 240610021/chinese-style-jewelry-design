import re, quopri, os

folder = r'g:\Downloads\蔡规划\琢匠产品'
f = os.path.join(folder, '001_1021446969579_1021446969579.mhtml')

with open(f, 'r', encoding='utf-8', errors='ignore') as fh:
    content = fh.read()

# 找到text/html部分
idx = content.find('Content-Type: text/html')
html_part = content[idx:]
blank = html_part.find('\n\n')
raw_qp = html_part[blank+2:]

# 分离第一个boundary之前的内容
boundary_idx = raw_qp.find('------MultipartBoundary')
if boundary_idx > 0:
    raw_qp = raw_qp[:boundary_idx]

# Decode quoted-printable
decoded = quopri.decodestring(raw_qp.encode('latin-1')).decode('utf-8', errors='ignore')

# 找body内容
body_match = re.search(r'<body[^>]*>(.*?)</body>', decoded, re.DOTALL | re.IGNORECASE)
if body_match:
    body = body_match.group(1)
    clean = re.sub(r'<script[^>]*>.*?</script>', '', body, flags=re.DOTALL | re.IGNORECASE)
    clean = re.sub(r'<style[^>]*>.*?</style>', '', clean, flags=re.DOTALL | re.IGNORECASE)
    clean = re.sub(r'<link[^>]*>', '', clean, flags=re.IGNORECASE)
    clean = re.sub(r'<noscript[^>]*>.*?</noscript>', '', clean, flags=re.DOTALL | re.IGNORECASE)
    clean = re.sub(r'\s+', ' ', clean).strip()
    print(f'BODY内容长度(去标签后): {len(clean)} 字符')
    print()
    print(clean[:2000])
    print()
    print(f'...共{len(clean)}字符')
else:
    print('未找到body标签')

external_css = re.findall(r'href="(https?://[^"]+\.css)"', decoded)
print(f'\n外部CSS引用数: {len(external_css)}')
for css in external_css[:5]:
    print(f'  {css}')

# 检查内嵌资源
embedded_resources = re.findall(r'------MultipartBoundary', content)
print(f'\nMHTML内嵌资源块数: {len(embedded_resources)}')