"""Entry point for cert-checker CLI."""

from cert_checker.cli import cli


def main() -> None:
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()
