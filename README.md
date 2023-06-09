# infoenergia-api

## Description
Api to exchange measurements and curves information

## Prerequisites
Before you begin, ensure you have met the following requirements:
* You must have at least `python 3.8`. You can get this python version through [pyenv](https://github.com/pyenv/pyenv#installation).
* You should have installed [pipenv](https://pipenv.readthedocs.io/en/latest/#install-pipenv-today).
* You should have a `Linux/Mac` machine. Windows is not supported and we are not thinking in it.
* An `nginx` installation.
* Optionally, an user with sudo permissions.

## Development setup

### Install application dependencies
```bash
# Clone the application
git clone git@github.com:Som-Energia/infoenergia-api.git .

# Change directory to the application folder
cd infoenergia-api

# Install pipenv
pip install --user pipenv

# Create a virtual environment for Python 3.8, 3.9 or 3.10
pipenv --python 3.8

# Install setuptools, for Python 3.8 or Python 3.9 only
pipenv run pip install --upgrade --force-reinstall setuptools

# Install application dev dependencies
pipenv install --dev

# Clear cache lock file for troubleshooting dependencies
pipenv lock --pre --clear

# Create the application environment file
cp .env.example .env
```

### Install a redis server
You can use a docker image:
```bash
docker run redis
```

or install at operating system level:
```bash
sudo apt install redis-server
```

### Configure the application
Edit the `.env` file:

- Note: Somenergia's credentials can be found in our private documentation.
- Configure `ERP_CONF` pointing to your ERP instance
- Configure `MONGO_CONF` pointing to your Mongo instance
- Configure `ERP_DB_CONF` pointing to your erp database
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
# From the root infoenergia-api repository directory.
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
pipenv run pytest
```

## Upgrading dependencies

```bash
pipenv install package # Use --dev for development dependencies
pipenv lock  # To upgrade all versions, add --keep-lock to just add the new deps
```

## Release protocol

- Determine the nes semantic version `M.m.r`
- Update version at `infoenergia_api/__init__.py`
- Update changelog at `CHANGES.md`
- Commit with "bump to vM.m.r"
- Tag the commit with `vM.m.r`

## Server deployment

### Installation

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
user@host:> cp .env.example .env
user@host:> vim .env
```

## Usage

You can simply execute `pipenv run python run.py` and the api will be ready to accept requests


## Changes

Take a look to [CHANGES.md](CHANGES.md) to see the historic of changes that has had this awesome api 🎉

## Contact
If you want to contact with us, feel free to send an email to <info@somenergia.coop>.

## License
This project uses the following license: [GNU AFFERO GENERAL PUBLIC LICENSE](LICENSE).
