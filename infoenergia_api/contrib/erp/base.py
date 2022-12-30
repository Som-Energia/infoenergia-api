import asyncio

from .manager import get_erp_instance


class BaseModel:

    model_name = None

    fields_map = None

    @classmethod
    async def create(cls, id_=None, name=None):
        self = cls()
        self._erp = get_erp_instance()
        self._loop = asyncio.get_event_loop()
        self._Model = self._erp.model(self.model_name)

        if id_:
            raw_instance = await self.read_from_erp(id_)
        elif name:
            raw_instance = await self.read_from_erp(name)

        for field, value in raw_instance.items():
            if self.fields_map:
                if field in self.fields_map:
                    setattr(self, self.fields_map[field], value)
            else:
                setattr(self, field, value)

        return self

    async def read_from_erp(self, field_key) -> dict:
        raw_instance = {}
        try:
            if isinstance(field_key, int):
                raw_instance = await self._loop.run_in_executor(
                    None, self._Model.read, field_key
                )

            if isinstance(field_key, str):
                instance_ids = await self._loop.run_in_executor(
                    self._Model.search, [("name", "=", field_key)]
                )
                if not instance_ids:
                    return {}
                raw_instance = await self._loop.run_in_executor(
                    self._Model.read(instance_ids[0])
                )
        finally:
            pass
        return raw_instance
