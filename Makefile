.PHONY: validate strict-validate test shellcheck actionlint media-smoke integration-setup integration-check install-codex-skill

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

integration-setup:
	scripts/setup_optional_integrations.sh

integration-check:
	python scripts/check_optional_integrations.py --allow-missing

install-codex-skill:
	scripts/install_codex_skill.sh
