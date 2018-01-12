all:
	preview

.PHONY: deploy staging update preview

preview:
	python3 compile.py preview && \
	cd published && \
	python3 -m http.server 8889

# usage: make deploy m="commit message"
deploy:
	python3 compile.py production && \
	cd ../tedxberkeley.github.io && \
	git pull --force && \
	cp -r ../TEDxBerkeley-2018/published/* . && \
	git add . && \
	git commit -m "deploy: $(m)" --allow-empty && \
	git push

