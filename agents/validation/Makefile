DOCKER_REGISTRY ?= docker.io
PORT ?= 9203
REPO ?= auto-ran/validation-agent
VERSION ?= $(shell git describe --tags --always --abbrev --dirty)
IMAGE_TAG := $(DOCKER_REGISTRY)/$(REPO):$(VERSION)

.PHONY: build run clean

build:
	@echo "Building Validation Agent Docker image with tag: $(IMAGE_TAG) - Version: $(VERSION)"
	docker build $(if $(NO_CACHE),--no-cache) \
		--build-arg VERSION=$(VERSION) \
		--tag $(IMAGE_TAG) .
	@echo "Validation Agent Docker image built successfully."

run:
	docker run --rm \
		-it \
		--env-file .env \
		--network host \
		-p $(PORT):$(PORT) \
		$(IMAGE_TAG)

clean:
	docker rmi $(IMAGE_TAG) || true
