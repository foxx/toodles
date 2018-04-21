SHELL := bash
MAKEFLAGS += --warn-undefined-variables
.SHELLFLAGS := -eu -o pipefail -c
DOCKER_TAG := toodles:latest


.PHONY: all
all:


.PHONY: build
build:
	docker build -t $(DOCKER_TAG) .


.PHONY: shell
shell: build
	docker run \
		--rm \
		-it \
		-p 8080:8080 \
		-v `pwd`:/toodles \
		$(DOCKER_TAG) \
		/bin/bash -i


.PHONY: test
test: build
	docker run \
		--rm \
		-it \
		-p 8080:8080 \
		-v `pwd`:/toodles \
		$(DOCKER_TAG) \
		pipenv run python3 -m pytest
