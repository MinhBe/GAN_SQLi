import os, re, sys
from spellchecker import SpellChecker

spell = SpellChecker()
d = r'C:\Projects\GAN_SQLi\Skill\output_txt'
files = sorted(os.listdir(d))

TECH = set("""
gan seqgan wgan cgan dcgan lsgan began infogan acgan
cnn rnn lstm gru svm knn rf xgboost adaboost
sql sqli ids nids hids android malware botnet
overfitting underfitting preprocessing hyperparameter autoencoder
backpropagation softmax relu tanh sigmoid dropout batchnorm
intrusion detection cyber adversarial generative
discriminator generator policy gradient reinforcement
obervability ddos dos xss csrf vulnerability exploit
supervised unsupervised semisupervised selfsupervised
imbalanced oversample undersample classifier classifiers
optimizer optimization regularization normalization
convolutional recurrent transformer attention encoder decoder
latent embedding representation discriminative
stochastic deterministic monte carlo variational
wasserstein earth mover distance emd jensen shannon
divergence kullback leibler kl js mmd gp
vae ae mlp dnn ann dbn rbm gans
synthesize synthesized synthetic augmentation
probabilistic likelihood posterior prior inference
anomaly outlier novelty fraud spam phishing
benchmark kaggle cifar mnist imagenet coco
methodology methodologies empirical theoretical
qualitative quantitative ablation sensitivity
robustness generalization convergence divergence
gradient descent adam sgd adagrad adadelta rmsprop
network neural deep learning artificial intelligence
machine data science analytics mining
information knowledge insight pattern trend
anomaly detection prediction classification regression
clustering dimensionality reduction selection extraction
nlp cv speech audio video image text signal
resnet vgg inception xception mobilenet shufflenet
yolo ssd faster rcnn maskrcnn retinanet densenet
bert gpt t5 bart roberta electra albert distilbert
transformer vit swin beit mae clip ddpm
feature instance sample batch epoch iteration
sota baseline stateoftheart endtoend pretrained finetune
multitask crossvalidation kfold hyperopt bayesian
roc auc f1 precision recall accuracy specificity
over under pre post hyper fine tune tuning
""".strip().split())

# Vietnamese words
VI_WORDS = {
    'các', 'của', 'và', 'một', 'cho', 'trong', 'được', 'với', 'có', 'không',
    'công', 'nghệ', 'thông', 'tin', 'dữ', 'liệu', 'mạng', 'học', 'máy',
    'nghiên', 'cứu', 'phát', 'triển', 'phương', 'pháp', 'đại', 'đà', 'nẵng',
    'trường', 'khoa', 'báo', 'cáo', 'tổng', 'kết', 'tài', 'cơ', 'sở',
    'mô', 'hình', 'xử', 'lý', 'mất', 'cân', 'bằng', 'dự', 'đoán', 'lỗi',
    'phần', 'mềm', 'ứng', 'dụng', 'mạng', 'sinh', 'đối', 'kháng', 'tấn', 'công',
    'đánh', 'lừa', 'bài', 'toán', 'dữ', 'liệu', 'đa', 'phương', 'tiện',
    'nhân', 'vật', 'trò', 'chơi', 'pokemon', 'veekun',
}


def is_vietnamese(words):
    return sum(1 for w in words if w.lower() in VI_WORDS) >= 5


def check_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    name = os.path.basename(path)
    words = re.findall(r'[a-zA-Z]+', content)

    if is_vietnamese(words):
        return check_vietnamese(name, content)
    else:
        return check_english(name, content)


def check_vietnamese(name, content):
    issues = []
    lines = content.split('\n')

    # Check for mojibake in Vietnamese text
    vi_pattern = re.compile(r'[^\x20-\x7E\xC0-\u024F\u1E00-\u1EFF\n\r\.\,\;\:\!\?\(\)\[\]\{\}\-\–\—\'\"]')
    bad_chars = set()
    for line in lines:
        for c in vi_pattern.findall(line):
            bad_chars.add(c)

    # Sample some problematic lines
    samples = []
    for i, line in enumerate(lines):
        if vi_pattern.search(line):
            samples.append((i + 1, line.strip()[:120]))
            if len(samples) >= 8:
                break

    if bad_chars:
        issues.append((f'Tieng Viet bi loi: {len(bad_chars)} ky tu dac biet', samples))

    return issues


def check_english(name, content):
    issues = []
    words = re.findall(r'[a-zA-Z]+', content)
    eng_words = [w.lower() for w in words if len(w) > 3 and w.isalpha()]

    # Check for concatenated words (no spaces)
    concat = re.findall(r'[a-z]{2,}[A-Z][a-z]{2,}', content)
    if concat and len(concat) > 5:
        samples = [(i + 1, line.strip()[:100])
                   for i, line in enumerate(content.split('\n'))
                   if re.findall(r'[a-z]{2,}[A-Z][a-z]{2,}', line.strip())][:5]
        issues.append((f'{len(concat)} tu bi dinh vao nhau (thieu space)', samples))

    # Spell check
    misspelled = set()
    for w in eng_words:
        if w not in TECH and w not in spell:
            misspelled.add(w)

    if misspelled and len(misspelled) < 60:
        real_issues = []
        for m in sorted(misspelled)[:15]:
            for line in content.split('\n'):
                if m in line.lower():
                    idx = line.lower().index(m)
                    ctx = line[max(0, idx - 30):idx + len(m) + 30].strip()
                    if len(ctx) > 100:
                        ctx = ctx[:100]
                    real_issues.append((m, ctx))
                    break
        if real_issues:
            issues.append((f'Loi chinh ta TA ({len(misspelled)} tu nghi van)', real_issues))

    return issues


sys.stdout.buffer.write(('=' * 70 + '\n').encode('utf-8'))
sys.stdout.buffer.write(b'KIEM TRA CHINH TA & OCR\n')
sys.stdout.buffer.write(('=' * 70 + '\n\n').encode('utf-8'))

for fname in files:
    path = os.path.join(d, fname)
    issues = check_file(path)
    if issues:
        sys.stdout.buffer.write((fname + '\n').encode('utf-8'))
        for title, samples in issues:
            sys.stdout.buffer.write(('  \u2716 ' + title + '\n').encode('utf-8'))
            for ln, txt in samples:
                safe = txt.encode('utf-8', errors='replace')
                sys.stdout.buffer.write(('    L' + str(ln) + ': ' + safe.decode('utf-8', errors='replace') + '\n').encode('utf-8', errors='replace'))
        sys.stdout.buffer.write(b'\n')
