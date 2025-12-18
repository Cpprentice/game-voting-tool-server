import asyncio
from faststream.rabbit import RabbitBroker

async def main():
    async with RabbitBroker() as br:
        await br.publish("message", "test")

if __name__ == '__main__':
    asyncio.run(main())
