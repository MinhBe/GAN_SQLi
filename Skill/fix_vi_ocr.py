import os, sys, re

d = r'C:\Projects\GAN_SQLi\Skill\output_txt'

# === FIX DHVH FILE ===
path = os.path.join(d, 'DHVH-2023-03.KHCN-Ha Thi Minh Phuong.txt')
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

changes = []

# Fix "e£" -> "et" (OCR misread of "et" in "et al.")
p1 = content.count('e£')
if p1:
    content = content.replace('e£', 'et')
    changes.append(f"'e£' -> 'et' ({p1} lan)")

# Fix "e‡" -> "et" 
p2 = content.count('e‡')
if p2:
    content = content.replace('e‡', 'et')
    changes.append(f"'e‡' -> 'et' ({p2} lan)")

# Fix "eÌ" -> "al" (from "et al.")
p3 = content.count('eÌ')
if p3:
    content = content.replace('eÌ', 'et al.')
    changes.append(f"'eÌ' -> 'et al.' ({p3} lan)")

# Fix "aÌ" -> "al"
p4 = content.count('aÌ')
if p4:
    content = content.replace('aÌ', 'al')
    changes.append(f"'aÌ' -> 'al' ({p4} lan)")

# Fix "ai." -> "al." (in "et al.")
p5 = content.count('ai.')
if p5:
    content = content.replace('ai.', 'al.')
    changes.append(f"'ai.' -> 'al.' ({p5} lan)")

# Fix "S§" -> "S."
p6 = content.count('S§')
if p6:
    content = content.replace('S§', 'S.')
    changes.append(f"'S§' -> 'S.' ({p6} lan)")

# Fix "©" in email -> "@"
if '©vku.udn.vn' in content:
    content = content.replace('©v', '@v')
    changes.append("'©' -> '@' (email)")

# Fix "oƒ" -> "of"
p7 = content.count('oƒ')
if p7:
    content = content.replace('oƒ', 'of')
    changes.append(f"'oƒ' -> 'of' ({p7} lan)")

# Fix "Jn‡elligent data analpsis" -> "Intelligent data analysis"
if 'Jn‡elligent data analpsis' in content:
    content = content.replace('Jn‡elligent data analpsis', 'Intelligent data analysis')
    changes.append("'Jn‡elligent data analpsis' -> 'Intelligent data analysis'")

# Fix "Á systematic" -> "A systematic"
if 'Á systematic' in content:
    content = content.replace('Á systematic', 'A systematic')
    changes.append("'Á systematic' -> 'A systematic'")

# Fix "Sha]ju Stephen" -> "Shaju Stephen"
if 'Sha]ju Stephen' in content:
    content = content.replace('Sha]ju Stephen', 'Shaju Stephen')
    changes.append("'Sha]ju Stephen' -> 'Shaju Stephen'")

# Fix "Vang e£ ai" -> "Yang et al." 
if 'Vang et al.' in content:
    content = content.replace('Vang et al.', 'Yang et al.')
    changes.append("'Vang' -> 'Yang'")

# Fix "Nam e‡ al" -> "Nam et al."
# Already handled by e‡ -> et above

# Fix "4.4‹" -> "4.4 "
if '4.4‹' in content:
    content = content.replace('4.4‹', '4.4 ')
    changes.append("'4.4‹' -> '4.4 '")

# Fix "PROMISE ¡ KC2" -> "PROMISE KC2"
if 'PROMISE ¡ KC2' in content:
    content = content.replace('PROMISE ¡ KC2', 'PROMISE KC2')
    changes.append("'PROMISE ¡ KC2' -> 'PROMISE KC2'")

# Fix "l§" in equation context (l§ at end of line)
if 'l§' in content:
    content = content.replace('l§', 'l')
    changes.append("'l§' -> 'l'")

# Fix "¡" (inverted exclamation mark used as stray char)
content = content.replace('¡ ', ' ')
content = content.replace('¡\n', '\n')

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

for c in changes:
    sys.stdout.buffer.write((c + '\n').encode('utf-8'))

sys.stdout.buffer.write(b'\n=== DHVH FIX DONE ===\n\n')

# === FIX PHUONG PHAP FILE ===
path2 = None
for f in os.listdir(d):
    if 'phuong_phap' in f.lower() and f.endswith('.txt'):
        path2 = os.path.join(d, f)
        break

if path2:
    with open(path2, 'r', encoding='utf-8') as f:
        content = f.read()

    changes2 = []

    # Fix "Đặng Hc"›ng Quang" -> "Đặng Hoàng Quang"
    # The issue is: Hc" + › + ng where › is a stray char
    if 'Đặng Hc' in content:
        content = content.replace('Đặng Hc"', 'Đặng H')
        content = content.replace('Đặng H›ng', 'Đặng Hoàng')
        changes2.append("'Đặng Hc\"›ng Quang' -> 'Đặng Hoàng Quang'")

    # Fix "lnem tra tự ®ng" -> "Kiểm tra tự động"
    # Actually "lnem" could be "Kiểm" OCR'd badly... but looking at the context,
    # the full line is about IDS automatic checking
    if 'lnem tra tự ®ng' in content:
        content = content.replace('lnem tra tự ®ng', 'Kiểm tra tự động')
        changes2.append("'lnem tra tự ®ng' -> 'Kiểm tra tự động'")

    # Fix "Ị)llảlIIl" -> "phẩm" (likely from sản phẩm)
    if 'Ị)llảlIIl' in content:
        content = content.replace('Ị)llảlIIl', 'phẩm')
        changes2.append("'Ị)llảlIIl' -> 'phẩm'")

    # Fix "„ Loại" -> "  Loại"
    if '„ Loại' in content:
        content = content.replace('„ Loại', '  Loại')
        changes2.append("'„ Loại' -> '  Loại'")

    # Fix "-.'›l 94" -> page break artifact, remove
    if "-.'›l 94" in content:
        content = content.replace("-.'›l 94", "")
        changes2.append("'-.\'›l 94' -> removed")

    # Fix "¡ Neural" -> "Neural"
    if '¡ Neural' in content:
        content = content.replace('¡ Neural', 'Neural')
        changes2.append("'¡ Neural' -> 'Neural'")

    # Fix "§. Han" -> "S. Han"
    if '§. Han' in content:
        content = content.replace('§. Han', 'S. Han')
        changes2.append("'§. Han' -> 'S. Han'")

    # Fix "H §S. Anderson" -> "H. S. Anderson"
    if '§S. Anderson' in content:
        content = content.replace('§S. Anderson', 'S. Anderson')
        changes2.append("'§S. Anderson' -> 'S. Anderson'")

    # Fix "l§th ACM" -> "th ACM"
    if 'l§th ACM' in content:
        content = content.replace('l§th ACM', 'th ACM')
        changes2.append("'l§th ACM' -> 'th ACM'")

    # Other general cleanup
    for old, new in [
        ('oƒ ', 'of '),
        ('e£ ', 'et '),
        ('\xad', ''),  # soft hyphen
    ]:
        if old in content:
            content = content.replace(old, new)

    with open(path2, 'w', encoding='utf-8') as f:
        f.write(content)

    for c in changes2:
        sys.stdout.buffer.write((c + '\n').encode('utf-8'))

    sys.stdout.buffer.write(b'\n=== PHUONG PHAP FIX DONE ===\n')
