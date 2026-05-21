PYTHON ?= python

.PHONY: help figures main appendix audit thesis clean-figures install

help:
	@echo "Targets:"
	@echo "  install    Install pinned Python dependencies"
	@echo "  figures    Rebuild every figure and table from existing processed data"
	@echo "  main       Run main analysis scripts (paper body)"
	@echo "  appendix   Run robustness and appendix scripts"
	@echo "  audit      Run the post-submission audit scripts (RESULTS.md row 5)"
	@echo "  thesis     Compile thesis.pdf via latexmk"
	@echo "  clean-figures  Remove generated figures (keeps source CSVs)"

install:
	$(PYTHON) -m pip install -r requirements.txt

figures: main appendix

main:
	$(PYTHON) run_pipeline.py --skip-pipeline

appendix:
	$(PYTHON) run_pipeline.py --appendix-only

audit:
	$(PYTHON) scripts/appendix/19_audit_github_diff_in_rdd.py
	$(PYTHON) scripts/main/15_outlier_sensitivity_bar.py

thesis:
	latexmk -pdf -interaction=nonstopmode thesis.tex

clean-figures:
	rm -f results/figures/*.png
