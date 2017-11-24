all:
	preview

.PHONY: deploy staging update preview

preview:
	python compile.py preview && \
	cd published && \
	python -m http.server 8889

# usage: make deploy m="commit message"
deploy:
	python compile.py production && \
	cd ../cs189.github.io && \
	git pull --force && \
	cp -r ../staging/published/* . && \
	cp ../staging/published/.gitignore . && \
	git add . && \
	git commit -m "deploy: $(m)" --allow-empty && \
	git push

