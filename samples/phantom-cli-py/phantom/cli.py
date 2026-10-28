import click
import requests

@click.command()
def main():
    """Run Phantom daemon."""
    click.echo("Phantom CLI daemon listening on ghost pipe...")

if __name__ == "__main__":
    main()
