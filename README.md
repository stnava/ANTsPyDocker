An attempt at making a portable ANTsPy docker app

```
docker build --build-arg WHEN=2019-07-10 -t  antspy .
```

Notes:
```
docker tag local-image:tagname reponame:tagname
docker push reponame:tagname

 docker tag antspy:latest stnava/antspy:latest
 docker push  stnava/antspy:latest

 docker run -i -t --rm antspy:latest
```

to clean

```
docker system df
docker system prune -a
```

Users should run


```
docker run -p 8888:8888 antspy:latest
```


to build a release that can be downloaded by this container:

```
docker run --user root -e GRANT_SUDO=yes -i -t --name=zoop jupyter/tensorflow-notebook /bin/bash
```

then run the (right) dockerfile contents in the container to build the wheel ... then upload.


```
docker cp CONTAINERID:/foo.whl foo.whl
```
