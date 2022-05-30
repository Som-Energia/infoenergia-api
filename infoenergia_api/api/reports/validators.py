from dataclasses import dataclass


@dataclass
class ReportsBody:
	id: int
	contract_ids: list
	type: str
	create_at: str
	month: str
