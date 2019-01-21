# Docker image building
* Run `docker build -t zgod/meta_rest_api .` inside the project root directory.
* Run `docker save zgod/meta_rest_api > meta_rest_api.tar.gz` to save the docker image as tar file.

# Docker deployment
* Download the meta_rest_api.tar.gz file.
* docker load --input meta_rest_api.tar.gz
* Deploy container docker run -d --rm -p 8081:8081 zgod/meta_rest_api
* Deploy as a service in docker swarm `docker service create --name meta_rest_api -p 8081:8081 zgod/meta_rest_api`