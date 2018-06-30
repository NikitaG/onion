# -*- coding: utf-8 -*-

"""Console script for wikidata_extractor."""
import sys
import click

@click.command()
@click.option('--file', default="-", help='Input file to push to message broker, by default stdin')
@click.option('--frontend_address', default="tcp://127.0.0.1:5551", help='Message broker frontend address.')
@click.option('--mode', default="simple", help='Pusher mode: simple - push line by line, json - push large json array file.')
@click.option('--compress', default="none", help='Whether input file compressed. Available options: none, bzip2, gzip')
def pusher(file, frontend_address, mode, compress):
    """Console script for pusher."""
    from onion.frontend import Pusher, PusherMode, PusherCompress
    pusher = Pusher(frontend_address, PusherMode(mode))
    pusher.push(file, PusherCompress(compress))
    return 0


@click.command()
@click.option('--frontend_port', default=5551, help='Frontend port for message broker.')
@click.option('--backend_port', default=5552, help='Backend port for message broker.')
def broker(frontend_port, backend_port):
    """Console script for running message broker"""
    from onion.server import Broker
    
    click.echo("Running messaging broker...")
    # click.echo("Frontend port: %d" % frontend_port)
    # click.echo("Backend port: %d" % backend_port)
    broker = Broker(frontend_address="tcp://*:%d" % frontend_port,
                    backend_address="tcp://*:%d" % backend_port)
    broker.run()
    return 0


if __name__ == "__main__":
    sys.exit(broker(5551, 5552))  # pragma: no cover
