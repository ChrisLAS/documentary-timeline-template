.PHONY: validate strict-validate test shellcheck actionlint media-smoke

validate:
	python scripts/validate_project.py .

strict-validate:
	python scripts/validate_project.py . --strict

test:
	python -m compileall -q scripts tests
	python -m unittest discover -s tests -v

shellcheck:
	shellcheck scripts/*.sh tests/*.sh

actionlint:
	actionlint

media-smoke:
	bash tests/smoke_media_pipeline.sh
