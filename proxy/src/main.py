import dagger
from dagger.mod import Annotated, Doc, field, function, object_type

NGINX_CONFIG = "/etc/nginx/conf.d/default.conf"

def init() -> dagger.Container:
    return (
        dagger.container().from_("nginx")
        .with_entrypoint([])
        .with_exec(['sh', '-c', f'echo "" > {NGINX_CONFIG}'])
    )

@object_type
class Proxy:
    """Forwards multiple services into a single service with multiple ports"""

    ctr: Annotated[
            dagger.Container,
            Doc("Internal proxy container"),
    ] = field(default=init())

    @function
    def with_service(
        name: str,
        frontend: int,
        backend: int,
        foo: dagger.Service
    ) -> "Proxy":
        """Add a service to proxy"""
   #     ports = await service.ports()
   #     port = await ports[0].port()
        cfg = get_config(backend, name, frontend)

        ctr = self.ctr.with_service_binding(name, foo).with_exposed_port(frontend)
        self.ctr = ctr.with_exec(['sh', '-c', f'echo "{cfg}" >> {NGINX_CONFIG}'])

        return self

    @function
    def service() -> dagger.Service:
        """Get the proxy Service"""
        ctr = self.ctr.with_exec(["/docker-entrypoint.sh", "nginx", "-g", "daemon off;"])
        return ctr.as_service()

def get_config(port: int, name: str, frontend: int) -> str:
    return f'''
server {{
    listen {frontend};
    listen [::]:{frontend};

    server_name {name};

    location / {{
        proxy_pass http://{name}:{port};
    }}
}}'''
