import asyncio

from faststream import FastStream
from faststream.rabbit import RabbitBroker

broker = RabbitBroker("amqp://guest:guest@localhost:5672/")

app = FastStream(broker)


@broker.subscriber("test")
async def base_handler(body):
    print(body)

if __name__ == '__main__':
    asyncio.run(app.run())