"""Validate generated SVGs and version README URLs by their content hash."""
import hashlib
from pathlib import Path
import re
import xml.etree.ElementTree as ET

readme = Path('README.md')
text = readme.read_text(encoding='utf-8')
for filename, alt in (
    ('stats.svg', 'GitHub 활동 통계와 활동 등급: 스타, 커밋, PR, 이슈, 기여 저장소'),
    ('top-langs.svg', '공개 저장소의 사용 언어 비율'),
):
    path = Path('profile') / filename
    content = path.read_bytes()
    root = ET.fromstring(content)
    if root.tag != '{http://www.w3.org/2000/svg}svg':
        raise ValueError(f'{path} is not an SVG')
    visible_text = ' '.join(root.itertext()).lower()
    if any(message in visible_text for message in (
        'something went wrong', 'rate limit', 'could not resolve', 'error!!!'
    )):
        raise ValueError(f'{path} contains an error card')
    revision = hashlib.sha256(content).hexdigest()[:16]
    url = f'https://raw.githubusercontent.com/sin-ibeom/sin-ibeom/main/profile/{filename}?v={revision}'
    pattern = r'(<img\b[^>]*\bsrc=")[^"]*("[^>]*\balt="' + re.escape(alt) + r'"[^>]*>)'
    text, count = re.subn(pattern, lambda m: m[1] + url + m[2], text)
    if count != 1:
        raise ValueError(f'Expected exactly one README image for {filename}, found {count}')
readme.write_text(text, encoding='utf-8')
