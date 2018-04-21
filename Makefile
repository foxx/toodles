SHELL := bash
MAKEFLAGS += --warn-undefined-variables
.SHELLFLAGS := -eu -o pipefail -c
DOCKER_TAG := toodles:latest


.PHONY: all
all:


.PHONY: dbuild
dbuild:
	docker build -t $(DOCKER_TAG) .


.PHONY: shell
dshell: dbuild
	docker run \
		--rm \
		-it \
		-p 8080:8080 \
		-v `pwd`:/toodles \
		$(DOCKER_TAG) \
		/bin/bash -i


.PHONY: dtest
dtest: dbuild
	docker run \
		--rm \
		-it \
		-p 8080:8080 \
		-v `pwd`:/toodles \
		$(DOCKER_TAG) \
		make test

.PHONY: test
test:
	pipenv run python3 -m pytest
