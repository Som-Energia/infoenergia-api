# Changelog

### 2.4.4
- fixed measurement_point adquisition

### 2.4.3
- added magnitud attribute to f1_reactive_energy_kVArh

### 2.4.2
- Improve invoices collection by searching them by contract_id

### 2.4.1
- Fix missing download filters for cch curves

### 2.4.0

- Curve types (`tg_val`, `tg_fact`...) and curve backends (mongo/timescale)
  are now decoupled and backends can be configured for each type on runtime
- Indirect curve backends using ERP as proxy to access mongo or timescale have
    been dropped in favour of direct mongo and timescale backends
    - ERP backends had problems with large ids and they failed to lookup
      CUPS with different frontier point code (final 2 digits of the CUPS)
- All CCH curves behave now like P5D (notably P2, gennetabeta and autocons)
    - Filter `to_` includes de first measure taken the next day (at local 00:00)
    - Filter `from_` includes the first measure taken that day (at local 00:00)
      althought its measuring period belongs to the day before.
      Notice that if you call the api for consecutive dates intervals that
      measure at 00:00 will be repeated in both responses.
    - Output attribute `date` is not the measuring time but the start of the measuring period
	- ie. If at T2 we measure the kWh consumed since T1, `date` means T1
	- Some curves (gennetabeta and autocons) informed T2
	- Some other curves (P2) informed T2-1h to get T1 but for them T1 = T2-15minutes
    - Output attribute `date` timezone is UTC (some curves used local Madrid TZ)
    - Uninformed fields now are `null` instead of `false`
- Deploy notes:
    - New dependencies added, pip install required
    - New `ERP_DB_CONF` configuration to connect directly to the ERP db
    - New config variable `CURVE_TYPE_DEFAULT_BACKEND` to set a default curve
      backend: `mongo` or `timescale`.
    - New config variable `CURVE_TYPE_BACKENDS` to change the default curve
      backend for each type of curve.

### 2.3.0

- Move all logic to obtain the tariff prices to ERP
- Adapt tariff endpoints according to ERP function
- Open tariff endpoint
- Move tariff prices of a contract from tariff view to contracts view

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
