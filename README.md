# GAN_SQLi Rebuild MVP

Bản dựng lại từ đầu cho hướng nghiên cứu **Data-Centric SQL Injection Detection with Utility-Guided SeqGAN Enrichment**.

Repo này là pipeline phòng thủ/lab-only để chạy trên local hoặc Kaggle:

```text
corpus -> canonicalize -> lineage-safe split -> D0 baseline -> SeqGAN candidates -> quality gate -> selection -> review/retrain
```

## Safety scope

- Không scan URL ngoài Internet.
- Không khai thác hệ thống thật.
- Không chứa danh sách payload tấn công thực tế.
- Generated text chỉ là `Candidate`, không phải ground truth.
- Chỉ chạy behavioral validation trong lab cô lập do bạn sở hữu/được phép.

## Dataset format

Tối thiểu:

```csv
payload,label,source,attack_family,lineage_id
```

Nếu chưa có `source`, `attack_family`, `lineage_id`, script sẽ thêm giá trị mặc định/hash tạm.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
python scripts/run_mvp.py --config configs/experiment_mvp.yaml --input data/sample/toy_payloads.csv --out runs/toy
```

## Kaggle

Xem `docs/KAGGLE_RUN.md` và `notebooks/kaggle_mvp.ipynb`.
