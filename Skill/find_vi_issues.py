import os, sys, re

def sp(msg):
    sys.stdout.buffer.write((msg + '\n').encode('utf-8'))

d = r'C:\Projects\GAN_SQLi\Skill\output_txt'

allowed = re.compile(
    r'[^\x20-\x7E'
    r'\xC0-\u024F'
    r'\u1E00-\u1EFF'
    r'\n\r\.\,\;\:\!\?\(\)\[\]\{\}\-\u2013\u2014\u2018\u2019\u201C\u201D'
    r'\"\u0300-\u036F]'
)

for fname in sorted(os.listdir(d)):
    if 'DHVH' in fname or 'phuong_phap' in fname:
        path = os.path.join(d, fname)
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        sp(f'=== {fname} ===')
        count = 0
        for i, line in enumerate(lines):
            bad = allowed.findall(line)
            if bad:
                count += 1
                if count <= 40:
                    ln = i + 1
                    txt = line.rstrip('\n\r')
                    sp(f'  L{ln}: chars={"".join(bad)}  ctx={repr(txt[:200])}')
        sp(f'  Total problematic lines: {count}')
        sp('')
