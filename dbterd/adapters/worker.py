from dbterd.adapters.base import Executor


class DbtWorker(Executor):
    def __init__(self, ctx) -> None:
        super().__init__(ctx)

    def run(self, **kwargs):
        super().run(**kwargs)
