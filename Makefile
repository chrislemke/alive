IMAGE  := alive
CONTAINER := alive
export DOCKER_CONFIG := $(CURDIR)/.docker
export DOCKER_HOST := unix://$(HOME)/.colima/default/docker.sock
COMPOSE := docker compose

.PHONY: breed birth logs

breed:
	$(COMPOSE) build

birth:
	$(COMPOSE) up -d

logs:
	$(COMPOSE) logs -f
