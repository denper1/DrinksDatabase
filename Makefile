# Commands
PYTHON					:=python3.9
VIRTUALENV				:=. venv/bin/activate
REMOVE_VENV				:=rm -rf venv
CHECK_VENV				:=[ -d venv ]
PIP_UPDATE				:=pip install --upgrade pip setuptools wheel
INSTALL_REQUIREMENT		:=pip install -r requirements.txt
RUN_PRECOMMIT			:=pre-commit run --all-files --show-diff-on-failure
RUN_TEST				:=python -m pytest
RUN_TEST_COV			:=python -m pytest --cov-report term-missing
EXECUTE_SCRIPT 			:=python drinks_database.py
DROP_TABLES 			:=python drop_tables.py

virtualenv:
	if [ ! -f venv/bin/activate ]; then \
		${PYTHON} -m venv venv; \
	fi \

define check_venv
	if ${CHECK_VENV}; then \
		${VIRTUALENV}; \
		$1; \
	else \
		$1; \
	fi
endef

install-requirements:
	@${PIP_UPDATE}
	$(call check_venv, ${INSTALL_REQUIREMENT})

pre-commit:
	$(call check_venv, ${RUN_PRECOMMIT})

test:
	$(call check_venv, ${RUN_TEST})

test-cov:
	$(call check_venv, ${RUN_TEST_COV})

init: install-requirements

execute:
	$(call check_venv, ${EXECUTE_SCRIPT})

drop-tables:
	$(call check_venv, ${DROP_TABLES})