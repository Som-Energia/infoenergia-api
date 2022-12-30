from infoenergia_api.contrib.erp import TariffPrice


class TestTariffPrice:
    async def test__create_tariff__ok(
        self,
        # given a valid tariff_id
        _20TD_tariff_id,
    ):
        # when we create a tariff from an id
        tariff_price = await TariffPrice.create(_20TD_tariff_id)
        import ipdb

        ipdb.set_trace()
        # then we have an isntance of TariffPrice class
        assert isinstance(tariff_price, TariffPrice)
