KUBE_CONFIG := ~/.kube/config
DOCKER_REGISTRY ?= hub.bubbleran.com
VERSION ?= $(shell git describe --tags --always --abbrev --dirty)

PORT ?= 9202
REPO ?= orama/agents/nat-ran/monitoring-agent
TAG ?= latest
PWD := $(shell pwd)
IMAGE := $(DOCKER_REGISTRY)/$(REPO):$(TAG)

.PHONY: build run push clean

build:
	@echo "Building Monitor Agent Docker image with tag: $(IMAGE) - Version: $(VERSION)"
	docker build $(if $(NO_CACHE),--no-cache) \
		--build-arg VERSION=$(VERSION) \
		--tag $(IMAGE) .
	@echo "Monitor Agent Docker image built successfully."
run:
	docker run --rm \
		-it \
		--env-file .env \
		--network host \
		-p $(PORT):$(PORT) \
		-v "$(PWD)/.env:/app/agent/.env:ro" \
		-v $(KUBE_CONFIG):/root/.kube/config:ro \
		$(IMAGE)

push:
	@echo "Pushing Monitor Agent Docker image with tag: $(IMAGE)"
	docker push $(IMAGE)
	@echo "Monitor Agent Docker image pushed successfully."

clean:
	docker rmi $(IMAGE) || true

