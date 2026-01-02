import asyncio
from random import random
from time import sleep

from textual.app import App, ComposeResult
from textual.containers import Center, Middle
from textual.timer import Timer
from textual.widgets import Footer, ProgressBar




class IndeterminateProgressBar(App[None]):

    def compose(self) -> ComposeResult:
        yield ProgressBar(total=100)
        yield Footer()

    def on_mount(self) -> None:
        self.action_start()

    async def increment(self, value):
        self.query_one(ProgressBar).advance(value)


    def action_start(self) -> None:
        """Start the progress tracking."""
        #self.query_one(ProgressBar).update(total=100)
        for i in range(100):
            asyncio.create_task(slowTask(self))


async def slowTask(app):
    await asyncio.sleep(random() * 10)
    await app.increment()

if __name__ == "__main__":
    bar = IndeterminateProgressBar()
    bar.run()


