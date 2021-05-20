## How to spin up an ONI

Get latest version of oni-express

```shell script
git clone -b release-1.2.1.rc1 https://github.com/UTS-eResearch/oni-express
```

This will generate a folder oni-express

Change directories to oni-express. This will be the main working directory of an ONI

```shell script
cd oni-express
```

Copy sample config files
```shell script
cp -f ../sample-config/* config/
```

Move your OCFL repo
```shell script
mv ../ocfl-demos/ocfl .
```
Run docker-compose

```shell script
docker-compose up
```

Stop Docker
```shell script
docker-compose stop
```
