import asyncio
from typing import Optional, Any, NoReturn

import aioredis
from fastapi import WebSocket, WebSocketDisconnect, status

from ._connection import Connection
from .utils import clear_task


class WebSocketManager:
    def __init__(self, broker_channel) -> NoReturn:
        self.active_connections: list[Connection] = []
        self._send_tasks: list[asyncio.Task] = []
        self._main_task: Optional[asyncio.Task] = None
        self.broker: Optional[aioredis.client.PubSub] = None
        self.broker_channel: str = broker_channel

    async def _connect(self, connection: Connection) -> NoReturn:
        await connection.accept()
        self.active_connections.append(connection)

    def _disconnect(self, connection: Connection) -> NoReturn:
        self.active_connections.remove(connection)

    async def new_connection(
        self, websocket: WebSocket, conn_id: str, topic: Optional[str] = None
    ) -> Connection:
        connection = Connection(websocket, conn_id, topic)
        await self._connect(connection)
        return connection

    async def remove_connection(self, connection: Connection, code: int = status.WS_1000_NORMAL_CLOSURE) -> NoReturn:
        await connection.close(code)
        self._disconnect(connection)
    
    def raw_remove_connection(self, connection: Connection) -> NoReturn:
        """
        Use it after a `WebSocketDisconnect` exception.
        If `WebSocketDisconnect` exception has been raised, we do not
        need to call `connection.close()`
        """
        self._disconnect(connection)

    async def _send(self, topic: str, message: Any) -> NoReturn:
        for connection in self.active_connections:
            if connection.topic == topic:
                await connection.send_json(message)

    def send(self, topic: str, message: Any) -> NoReturn:
        self._send_tasks.append(asyncio.create_task(self._send(topic, message)))

    async def _to_broker(self, message: Any) -> NoReturn:
        await self.broker.publish(self.broker_channel, message)
    
    async def receive(self, message: Any) -> NoReturn:
        pass

    async def _from_broker(self) -> NoReturn:
        while True:
            message = await self.broker.get_message(ignore_subscribe_messages=True)
            self.send(message['channel'], message['data'])

    async def broadcast(self, message: Any) -> NoReturn:
        for connection in self.active_connections:
            await connection.send_json(message)
    
    async def startup(self) -> NoReturn:
        await self.broker.subscribe(self.broker_channel)
        self._main_task = asyncio.create_task(self._from_broker())

    async def shutdown(self) -> NoReturn:
        for task in self._send_tasks:
            clear_task(task)
        for connection in self.active_connections:
            await self.remove_connection(connection, code=status.WS_1012_SERVICE_RESTART)
        clear_task(self._main_task)
