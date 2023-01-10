#!/bin/sh

docker build -t wrh-org-image:prd -f Dockerfile .
if [ `echo $?` == 0 ]; then
	docker rm -f wrh-org
	docker run -dt --restart=always -p 8001:8001 --name wrh-org wrh-org-image:prd
fi

