import asyncio
import socket
import time

class DNSCache:
    def __init__(self, ttl: int = 60):
        self.ttl = ttl
        self._cache: dict[str, tuple[str, float]] = {}
        self._lock = asyncio.Lock()

    async def resolve(self, hostname: str) -> str:
        async with self._lock:
            if hostname in self._cache:
                ip, ts = self._cache[hostname]
                if time.monotonic() - ts < self.ttl:
                    print(f"[DNSCache] cache hit: {hostname} -> {ip}")
                    return ip

            loop = asyncio.get_event_loop()
            ip = await loop.run_in_executor(None, socket.gethostbyname, hostname)
            self._cache[hostname] = (ip, time.monotonic())
            print(f"[DNSCache] resolved: {hostname} -> {ip}")
            return ip

dns_cache = DNSCache(ttl=60)