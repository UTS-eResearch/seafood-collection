## Seafood Safety Group Arkisto

#### People
The Seafood Safety Group is led by [Shauna Murray](mailto:Shauna.Murray@uts.edu.au), and comprised of:
* [Penny Ajani](mailto:penelope.ajani@uts.edu.au): Does mathematical modelling from the data and has been primary contact for getting example data and discussing data pipeline
* [Hazel Farrell](mailto:hazel.farrell@dpi.nsw.gov.au): Partner from the NSW Department of Primary Industries who  helps clean and distribute the data


#### Data

The Seafood Safety Group has sensors (provided by *The Yield*) located in various estuaries around NSW, collecting data about the salinity, temperature, pressure and water depth at regular intervals.
This data is uploaded from the sensors to an Azure database and then downloaded in monthly csv files.
It is also currently available for consumers via a live website.

For testing purposes, a simple script has been written which generates sample data for each estuary and month from 2010-2020.
It's contained in the generated data directory and when run with `generate_data.py` creates sub-folders in the current directory containing both simulated raw data and the associated ro-crate-metadata.json file.

Run:
```shell script
python3 generate_data.py
```

It will create a `sensor-data` folder. After that's created, you can use the ro-crate-deposit script from [OCFL Demos](https://code.research.uts.edu.au/eresearch/ocfl-demos):

```shell script
git clone https://code.research.uts.edu.au/eresearch/ocfl-demos.git
cd ocfl-demos
npm install
```

Generate an OCFL
```shell script
node ro-crate-deposit.js --repo=ocfl --name seafood ../sensor-data/*
```
This will generate an ocfl directory called `ocfl-demos` in the same directory to create an ocfl repo called 'ocfl' which contains all of those RO-Crates and data.

Next step: Set up ONI

See [ONI.md](./ONI.md)

---

Directories:
* sample:
   Samples on how a single ro-crate file should look like
   Data sample provided by seafood group
* templates:
   python templates for generating datasets
* sample-config: Stores configuration files for ONI (should be copied into oni-express folder)
* api_calls:
  stores the code, api keys and data fetched from the various APIs that provide sensor data
  
The following directories will be created by the program:   
* sensor-data:
   Stores example RO-Crates
* ocfl-demos/ocfl:
   Stores the generated OCFL repository
