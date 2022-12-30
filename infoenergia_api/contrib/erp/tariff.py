from .base import BaseModel


class TariffPrice(BaseModel):

    model_name = "product.pricelist"

    fields_map = {"id": "id", "version_id": "version_id", "type": "type"}

    @classmethod
    async def create(cls, price_id):
        self = await super().create(id_=price_id)
        self._Priceversion = self._erp.model("product.pricelist.version")
        self._PricelistItem = self._erp.model("product.pricelist.item")

        return self

    def term_price(self, items_id, term_type, units):
        """
        Term price
         [{
         'period': P1
         'price': 0.139
         'units': €/kWh
         }]
        """
        fields = [
            "name",
            "base_price",
            "price_discount",
            "price_surcharge",
        ]

        item_price = self._PricelistItem.read(items_id, fields)
        if term_type == "GKWh":
            return [
                {
                    "period": self._get_period(tp["name"]),
                    "price": tp["base_price"] * (1 + tp["price_discount"])
                    + tp["price_surcharge"],
                    "units": units,
                }
                for tp in item_price
                if tp["name"].find(term_type) > 0
                if "P3" not in tp["name"]
            ]
        else:
            return [
                {
                    "period": self._get_period(tp["name"]),
                    "price": tp["base_price"] * (1 + tp["price_discount"])
                    + tp["price_surcharge"],
                    "units": units,
                }
                for tp in item_price
                if tp["name"].find(term_type) > 0
            ]

    def _get_period(self, price_name: str) -> str:
        return (
            price_name.split(" ")[1]
            if "2.0TD" in price_name
            else price_name.split("_")[0]
        )

    @property
    def price_detail(self):
        """
        Tariff prices
         2020-06-01
        """
        if not hasattr(self, "_price_detail"):
            fields = [
                "date_start",
                "date_end",
                "items_id",
            ]
            prices = self._Priceversion.read(
                self.version_id, fields, order="date_start"
            )

            if prices:
                self._price_detail = [
                    {
                        "dateStart": price["date_start"],
                        "dateEnd": price["date_end"],
                        "activeEnergy": self.term_price(
                            price["items_id"], "ENERGIA", "€/kWh"
                        ),
                        "power": self.term_price(
                            price["items_id"], "POTENCIA", "€/kW year"
                        ),
                        "GKWh": self.term_price(price["items_id"], "GKWh", "€/kWh"),
                    }
                    for price in prices
                ]

        return {"current": self._price_detail[0], "historic": self._price_detail[1:]}

    @property
    def tariff(self):
        if not hasattr(self, "_tariff") and self.type == "sale":
            self._tariff = {
                "tariffPriceId": self.id,
                "price": self.price_detail,
            }
        return getattr(self, "_tariff", None)
