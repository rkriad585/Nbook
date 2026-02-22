import click
from flask.cli import FlaskGroup
from core.terminal import run_server_secure, run_server_free, convert_notebook

def create_cli(app):
    
    @click.group()
    def cli():
        """Nbook: The Glass Interface Notebook"""
        pass

    @cli.command()
    def start():
        """Start Nbook in SECURE mode."""
        run_server_secure(app)

    @cli.command()
    def free():
        """Start Nbook in FREE mode."""
        run_server_free(app)

    @cli.command()
    @click.argument('filename')
    def convert(filename):
        """Convert .npy or .ngo to code folder."""
        success, msg = convert_notebook(filename)
        if success:
            click.echo(f"✅ Success! Converted to: {msg}")
        else:
            click.echo(f"❌ Error: {msg}")

    return cli
