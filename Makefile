.PHONY: build clean version license-headers remove-license-headers update-license-headers help

build: ## Build the project
	python setup.py sdist bdist_wheel

clean: ## Clean the build artifacts
	rm -r ./build ./dist ./*.egg-info

version: ## Update the version
	@if [ "$(shell git rev-parse --abbrev-ref HEAD)" != "master" ]; then \
		echo "You're not on the master branch."; \
		exit 1; \
	fi
	@if [ -z "$(TAG)" ]; then \
		echo "Please provide a version number. Example: make version TAG=version-number"; \
		exit 1; \
	fi
	sed -i "s/\(version=\)'[^']*'/\1'$(TAG)'/" setup.py
	git add setup.py
	-git commit -m "Change version to $(TAG)"
	git push origin master
	git tag -a "$(TAG)"
	git push origin "$(TAG)"

license-headers: ## Add license headers to files
	./license_headers.py add

remove-license-headers: ## Remove license headers from files
	./license_headers.py remove

update-license-headers: ## Update license headers in files
	./license_headers.py update

help: ## Display this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
