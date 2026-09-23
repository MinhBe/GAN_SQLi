test:
	pytest -q

toy:
	python scripts/run_mvp.py --config configs/experiment_mvp.yaml --input data/sample/toy_payloads.csv --out runs/toy
