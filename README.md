An attempt at making a portable ANTsPy docker app

```
docker build --build-arg WHEN=2019-05-01 -t  antspy .
```

#
# docker tag local-image:tagname reponame:tagname
# docker push reponame:tagname

 docker tag antspy:latest stnava/antspy:latest
 docker push  stnava/antspy:latest

# # Just create interactive container. No start but named for future reference.
# Use your own image.
docker create -it --name reck antspy

# Now start it.
docker start reck

# Now attach bash session.
docker exec -it reck bash
