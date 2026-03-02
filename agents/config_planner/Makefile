DOCKER_REGISTRY ?= docker.io
PORT ?= 9201
REPO ?= auto-ran/config-planner-agent
VERSION ?= $(shell git describe --tags --always --abbrev --dirty)
IMAGE_TAG := $(DOCKER_REGISTRY)/$(REPO):$(VERSION)

.PHONY: build run push clean

build:
	@echo "Building Config Planner Agent Docker image with tag: $(IMAGE_TAG) - Version: $(VERSION)"
	docker build $(if $(NO_CACHE),--no-cache) \
		--build-arg VERSION=$(VERSION) \
		--tag $(IMAGE_TAG) .
	@echo "Config Planner Agent Docker image built successfully."

run:
	docker run --rm \
		-it \
		--env-file .env \
		--network host \
		-p $(PORT):$(PORT) \
		$(IMAGE_TAG)

clean:
	docker rmi $(IMAGE_TAG) || true
