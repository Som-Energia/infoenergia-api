# infoenergia-api
Api to exchange measurements and curves information

#### Prerequisites

Before you begin, ensure you have met the following requirements:
* You must have at least `python 3.8`. You can get this python version through `pyenv`. See more here -> https://github.com/pyenv/pyenv#installation
* You should have installed `pipenv`. Instructions here -> https://pipenv.readthedocs.io/en/latest/#install-pipenv-today
* You should have a `Linux/Mac` machine. Windows is not supported and we are not thinking in it.
* An `nginx` installation
* Optionally, an user with sudo permissions

#### Installation

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

#### Usage

#### Changes
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
