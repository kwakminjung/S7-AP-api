import asyncio
import socket
import time

class DNSCache:
    def __init__(self, ttl: int = 60, retries: int = 3, retry_delay: float = 0.5):
        self.ttl = ttl
        self.retries = retries
        self.retry_delay = retry_delay
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
            last_error = None

            for attempt in range(1, self.retries + 1):
                try:
                    ip = await loop.run_in_executor(None, socket.gethostbyname, hostname)
                    self._cache[hostname] = (ip, time.monotonic())
                    print(f"[DNSCache] resolved: {hostname} -> {ip} (attempt {attempt})")
                    return ip
                except Exception as e:
                    last_error = e
                    print(f"[DNSCache] resolution failed for {hostname} on attempt {attempt}: {e}")
                    await asyncio.sleep(1)

            if hostname in self._cache:
                ip, _ = self._cache[hostname]
                print(f"[DNSCache] returning stale cache for {hostname} -> {ip}")
                return ip

            raise Exception(f"DNS resolution failed for {hostname} after {self.retries} attempts: {last_error}")

dns_cache = DNSCache(ttl=300, retries=3, retry_delay=0.5)