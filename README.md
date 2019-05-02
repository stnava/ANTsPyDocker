An attempt at making a portable ANTsPy docker app

```
docker build --build-arg WHEN=2019-05-01 -t  antspy .
```

#
# docker tag local-image:tagname reponame:tagname
# docker push reponame:tagname

 docker tag antspy:latest stnava/antspy:latest
 docker push  stnava/antspy:latest

# docker run -i -t --rm antspy:latest

# to clean
# docker system df
# docker system prune -a


Users should run


```
docker run -p 8888:8888 antspy:latest
```


