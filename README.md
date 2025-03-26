

### Docker <img alt="docker" width="26px" src="https://raw.githubusercontent.com/github/explore/80688e429a7d4ef2fca1e82350fe8e3517d3494d/topics/docker/docker.png" />

To run the application into kubernetes platform, it must be packaged in the right format which is a [docker container](https://www.docker.com/resources/what-container). A docker container can be initialized from a docker image, the instructions to build the docker image are at [`etc/docker/Dockerfile`](https://github.com/labvisio/is-face-detector/blob/master/etc/docker/Dockerfile).

To be available to the kubernetes cluster, the docker image must be stored on [dockerhub](https://hub.docker.com/), to build the image locally and push to dockerhub:

```bash
docker build -f etc/docker/Dockerfile -t <user>/is-face-detector:<version> .
docker push <user>/is-face-detector:<version>
```

The docker image used here supports any application in python that uses [OpenCV]. Your application may not run because the image docker doesn't contain some library, in this case it will be necessary to edit the [`etc/docker/Dockerfile`](https://github.com/labvisio/is-face-detector/blob/master/etc/docker/Dockerfile) and rebuild it to install what you need or to use another base image. 
