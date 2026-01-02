import asyncio
from time import sleep

from TestConsole import MenuApp

menuApp = MenuApp()

async def callback(result):
    menuApp.setMessage("This is a callback. " + result)
    tasks = []
    for i in range(100):
        tasks.append(asyncio.create_task(slowfunction()))

async def slowfunction():
    menuApp.increment()
    await asyncio.sleep(200)


menuApp.percentage = 0
menuApp.setList("Dit is een prompt:", ["Option 1", "Option 2", "Option 3"], callback)
menuApp.run()