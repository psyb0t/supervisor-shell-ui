.PHONY: version build all

all: license-headers version build

build:
	python setup.py sdist bdist_wheel

clean:
	rm -r ./build ./dist ./*.egg-info

version:
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

license-headers:
	./license_headers.py add

remove-license-headers:
	./license_headers.py remove

update-license-headers:
	./license_headers.py update
