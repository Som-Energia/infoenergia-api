# infoenergia-api
Api to exchange measurements and curves information

## Prerequisites

Before you begin, ensure you have met the following requirements:
* You must have at least `python 3.8`. You can get this python version through `pyenv`. See more here -> https://github.com/pyenv/pyenv#installation
* You should have installed `pipenv`. Instructions here -> https://pipenv.readthedocs.io/en/latest/#install-pipenv-today
* You should have a `Linux/Mac` machine. Windows is not supported and we are not thinking in it.
* An `nginx` installation
* Optionally, an user with sudo permissions

## Installation

First choose a directory where you want to install the api. We recommend install under `/opt` directory. This guide will use it as base directory installation

After that, clone repository from github:

```bash
user@host:> sudo mkdir -p /opt/infoenergia-api
user@host:> sudo chown user:user /opt/infoenergia-api
user@host:> cd /opt/infoenergia-api
user@host:> git clone git@github.com:Som-Energia/infoenergia-api.git .
```

Once code is downladed install requirements:
```bash
user@host:> pipenv install
```

With all requirements installed, it's time to configure our api. Copy `.env.example` to `.env` and with your favorite editor adapt it with the credentials and name that you will use
```bash
user@host:> mv .env.example .env
user@host:> vim .env
```

Now our api is ready to run. You can simply execute `pipenv run python run.py` and the api will be ready to accept requests

## Development setup

```bash
sudo apt install redis-server
git clone git@github.com:Som-Energia/infoenergia-api.git .
cd infoenergia-api
pip install --user pipenv
pipenv install --dev
cp .env.example .env
```

Edit the .env file:

- Note: Somenergia's credentials for ERP, Mongo and Beedata API can be found in private documentation dbconfig and infoenergia documentation.
- Configure `ERP_CONF` pointing to your ERP instance
- Configure `MONGO_CONF` pointing to your Mongo instance
- If the `ERP_CONF` "server" starts with http instead of https, set:
	```
	TRANSPORT_POOL_CONF={"secure": false}
	```
	Otherwise, set it `{"secure": true}`
- Configure `REDIS_CONF` as `redis://localhost:6379` (if you are using local redis)
- Point the `DATA_DIR` to an existing local directory to store the database file
- Given  Beedata API credentials:
	- Move certificate files locally and update `CERT_FILE` and `KEY_FILE` accordingly
	- Edit `USERNAME`, `PASSWORD`, `COMPANY_ID` and `BASE_URL` to the provided access parameters.


## Testing

Setup test data (Requires VPN access):

```bash
# From the directory containing infoenergia-api
git clone git@gitlab.somenergia.coop:IT/it-docs.git -o testdata
git clone git@gitlab.somenergia.coop:IT/somenergia-back2backdata.git
cd infoenergia-api/
ln -s ../somenergia-back2backdata/infoenergia-api/testdata
cd tests
ln -s ../../testdata/b2bs/json4test.yaml
cd ..
```

Then just:

```bash
$ pipenv run pytest
```

## Upgrading dependencies

pipenv install package # Use --dev for development dependencies
pipenv lock  # To upgrade all versions, add --keep-lock to just add the new deps

## Release process

- Determine the nes semantic version `M.m.r`
- Update version at `infoenergia_api/__init__.py`
- Update changelog at `README.md`
- Commit with "bump to vM.m.r"
- Tag the commit with `vM.m.r`

## Usage

## Changes

### 2.2.1
- fixed mock server

### 2.2.0

- Added cch curves `tg_gennetabeta` and `tg_cchautocons`
- Fix: empty points were returned if the name/CUPS was different
- Breaking change: all curves include the `to_` date
- Security: Limit the jwt decoding algorithms to avoid using RAW
  - This would enable an attacker bypassing token signature check
    by crafting a token whose signature is set to RAW

### 2.1.1
- TgCchP1 reads from tg_p1 collection

### 2.1.0
- F1 curves now are obtained from ERP instead of access directly to mongo
- Added attribute "tipo_medida" to contract information

### 2.0.1
- Add the magnitud of active energy (if its AE or AS)

### 2.0.0-rc1
- updated dependencies versions
- adapted code to that dependencies
- reimplemented report processing
- a lot of bugs fixed
- improved perfomance

### 1.5.0
- Adapted endpoints to new tolls


### 1.4.1
- Authentication fixes in report endpoint


### 1.4.0

- endpoint reports:
  - Post contracts to be processed
  - Download and save report information

- enpoint cch:
  - Add new filter: get cch by download date
  - Fix bugs:
    - get only 20 digits of cups
    - add cch type to pagination request

### 1.3.2

- endpoint modcontracts:
  - get modcontracts by contractId
  - make more intuitive to filter canceled contracts, now it takes into account end date of the contract and not the initial date
- endpoint contracts: return self-consumption type instead of True or False
- add number of total results to response for all endpoints

### 1.3.1
- Added tertiaryPowerHistory to contracts and modcontracts response

### 1.3.0
- Added f5d endpoint
- Support for parallel requests to one ERP

### 1.2.1
- Fixed minor bugs

### 1.2.0
- Implemented pagination results for all endpoints

### 1.1.1
- Add tariff to the f1 object
- kW/day -> kW

### 1.1.0
- New endpoint to get all contractual modifications

### 1.0.2
- Fix F1 filter by contractId
- Now we can filter invoices by date when getting when filtering by contractId

### 1.0.1
- Add extra filter to contract and f1 endpoints

#### Contact
If you want to contact with us, feel free to send an email to <info@somenergia.coop>.

#### License
This project uses the following license: [GNU AFFERO GENERAL PUBLIC LICENSE](LICENSE).
