import os, sys, re

d = r'C:\Projects\GAN_SQLi\Skill\output_txt'

def sp(msg):
    sys.stdout.buffer.write((msg + '\n').encode('utf-8'))

allowed = re.compile(r'[^\x20-\x7E\xC0-\u024F\u1E00-\u1EFF\n\r\.\,\;\:\!\?\(\)\[\]\{\}\-\u2013\u2014\u2018\u2019\u201C\u201D\"\u0300-\u036F]')

for fname in sorted(os.listdir(d)):
    if not ('DHVH' in fname or 'phuong_phap' in fname):
        continue

    path = os.path.join(d, fname)
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    sp(f'=== {fname} ===')

    # Count remaining issues
    count = 0
    for i, line in enumerate(lines):
        bad = allowed.findall(line)
        if bad:
            count += 1
            if count <= 15:
                ln = i + 1
                txt = line.rstrip()
                sp(f'  L{ln}: bad={"".join(bad)}  ctx={txt[:180]}')
    sp(f'  Con lai: {count} dong')

    # Verify specific fixes
    sp('')
    sp('  --- Kiem tra fix ---')
    checks = [
        'et al.',
        'S. M. Ghufran',
        'ntbinh@vku',
        'Hoàng Quang',
        'Kiểm tra tự động',
        'phẩm',
    ]
    for c in checks:
        for i, line in enumerate(lines):
            if c in line:
                ln = i + 1
                txt = line.rstrip()[:180]
                sp(f'  L{ln}: {txt}')
                break
        else:
            sp(f'  (not found: {c})')
    sp('')
