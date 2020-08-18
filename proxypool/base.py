class Proxy:
    def __init__(self, prefix, ip, port, source, is_elite=True):
        self.prefix = prefix
        self.ip = ip
        self.port = port
        self.is_elite = is_elite
        self.source = source

    def __str__(self):
        return f"{self.prefix}://{self.ip}:{self.port}__from{self.source}"
