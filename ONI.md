## How to spin up an ONI

Get latest version of oni-express

```shell script
git clone -b release-1.2.0.rc1 https://github.com/UTS-eResearch/oni-express.git
```

This will generate a folder oni-express

Get the latest version of oni-indexer

```shell script
git clone -b release-1.2.0.rc1 https://github.com/UTS-eResearch/oni-indexer.git
```

```
.../oni-express
.../oni-indexer

    ** It is crucial that these two repo's are sibling folders.
```

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
