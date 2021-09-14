import logging
from jaeger_client import Config


def init_tracer(service):
    logging.getLogger('').handlers = []
    logging.basicConfig(format='%(message)s', level=logging.DEBUG)

    config = Config(
        config={ # usually read from some yaml config
            'sampler': {
                'type': 'const',
                'param': 1,
            },
            'logging': True,
            'reporter_batch_size': 1,
            'local_agent': {
                'reporting_host': "192.168.3.20",
                'reporting_port': 5775,
            }
        },
        service_name=service,
    )

    # this call also sets opentracing.tracer
    return config.initialize_tracer()
