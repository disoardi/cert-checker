"""Command-line interface for cert-checker."""

from pathlib import Path
from typing import Optional

import click
from rich.console import Console

from cert_checker.checker.remote import RemoteCertChecker
from cert_checker.checker.validator import CertificateValidator
from cert_checker.config import Config
from cert_checker.store.converter import CertificateConverter
from cert_checker.store.keystore import KeystoreManager
from cert_checker.store.truststore import TruststoreManager
from cert_checker.utils.cert_parser import CertificateParser
from cert_checker.utils.display import DisplayFormatter

console = Console()
formatter = DisplayFormatter(console)


@click.group()
@click.version_option(version="0.1.0")
def cli() -> None:
    """cert-checker: Swiss Army knife for SSL/TLS certificate management."""
    pass


@cli.command()
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    help="Configuration file path",
)
@click.option("--host", "-h", help="Host FQDN to check")
@click.option("--port", "-p", type=int, default=443, help="Port number (default: 443)")
@click.option("--timeout", "-t", type=int, default=10, help="Connection timeout (default: 10)")
@click.option("--warning-days", "-w", type=int, default=30, help="Warning threshold in days")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
@click.option("--csv", "output_csv", is_flag=True, help="Output as CSV")
def check(
    config: Optional[Path],
    host: Optional[str],
    port: int,
    timeout: int,
    warning_days: int,
    verbose: bool,
    output_json: bool,
    output_csv: bool,
) -> None:
    """Check SSL/TLS certificates on remote hosts."""
    checker = RemoteCertChecker(timeout=timeout)

    if config:
        # Check hosts from config file
        try:
            cfg = Config.from_file(config)
            results = checker.check_all_hosts(cfg)
        except Exception as e:
            console.print(f"[bold red]Error loading config:[/bold red] {e}")
            raise click.Abort()
    elif host:
        # Check single host
        result = checker.check_host(host, port, warning_days)
        results = [result]
    else:
        console.print("[bold red]Error:[/bold red] Either --config or --host must be provided")
        raise click.Abort()

    # Output results
    if output_json:
        console.print(formatter.export_json(results))
    elif output_csv:
        console.print(formatter.export_csv(results))
    else:
        if len(results) == 1:
            formatter.format_check_result(results[0], verbose=verbose)
        else:
            formatter.print_summary_table(results)

            if verbose:
                console.print()
                for result in results:
                    formatter.format_check_result(result, verbose=True)


@cli.group()
def truststore() -> None:
    """Manage truststore (trusted certificates)."""
    pass


@truststore.command("list")
@click.option(
    "--store",
    "-s",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Truststore path",
)
@click.option("--password", "-p", help="Truststore password")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["jks", "pkcs12", "pem"], case_sensitive=False),
    default="jks",
    help="Truststore format",
)
def truststore_list(store: Path, password: Optional[str], format: str) -> None:
    """List certificates in truststore."""
    try:
        ts = TruststoreManager(path=store, password=password, format=format)
        entries = ts.list_certificates()

        if not entries:
            console.print("[yellow]No certificates found in truststore[/yellow]")
        else:
            formatter.print_truststore_table(entries)

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise click.Abort()


@truststore.command("add")
@click.option(
    "--store",
    "-s",
    type=click.Path(path_type=Path),
    required=True,
    help="Truststore path",
)
@click.option(
    "--cert", "-c", type=click.Path(exists=True, path_type=Path), required=True, help="Certificate file"
)
@click.option("--alias", "-a", required=True, help="Certificate alias")
@click.option("--password", "-p", help="Truststore password")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["jks", "pkcs12", "pem"], case_sensitive=False),
    default="jks",
    help="Truststore format",
)
def truststore_add(
    store: Path, cert: Path, alias: str, password: Optional[str], format: str
) -> None:
    """Add certificate to truststore."""
    try:
        # Load or create truststore
        if store.exists():
            ts = TruststoreManager(path=store, password=password, format=format)
        else:
            ts = TruststoreManager(password=password, format=format)

        # Import certificate
        actual_alias = ts.import_from_file(cert, alias)

        # Save truststore
        ts.save(store, password)

        console.print(
            f"[green]✓[/green] Certificate added successfully with alias: {actual_alias}"
        )

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise click.Abort()


@truststore.command("remove")
@click.option(
    "--store",
    "-s",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Truststore path",
)
@click.option("--alias", "-a", required=True, help="Certificate alias")
@click.option("--password", "-p", help="Truststore password")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["jks", "pkcs12", "pem"], case_sensitive=False),
    default="jks",
    help="Truststore format",
)
def truststore_remove(store: Path, alias: str, password: Optional[str], format: str) -> None:
    """Remove certificate from truststore."""
    try:
        ts = TruststoreManager(path=store, password=password, format=format)

        if ts.remove_certificate(alias):
            ts.save(store, password)
            console.print(f"[green]✓[/green] Certificate '{alias}' removed successfully")
        else:
            console.print(f"[yellow]Certificate '{alias}' not found[/yellow]")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise click.Abort()


@truststore.command("export")
@click.option(
    "--store",
    "-s",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Truststore path",
)
@click.option("--alias", "-a", required=True, help="Certificate alias")
@click.option(
    "--output", "-o", type=click.Path(path_type=Path), required=True, help="Output file path"
)
@click.option("--password", "-p", help="Truststore password")
@click.option(
    "--store-format",
    type=click.Choice(["jks", "pkcs12", "pem"], case_sensitive=False),
    default="jks",
    help="Truststore format",
)
@click.option(
    "--output-format",
    type=click.Choice(["pem", "der"], case_sensitive=False),
    default="pem",
    help="Output format",
)
def truststore_export(
    store: Path,
    alias: str,
    output: Path,
    password: Optional[str],
    store_format: str,
    output_format: str,
) -> None:
    """Export certificate from truststore."""
    try:
        ts = TruststoreManager(path=store, password=password, format=store_format)
        ts.export_certificate(alias, output, output_format)
        console.print(f"[green]✓[/green] Certificate exported to {output}")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise click.Abort()


@cli.group()
def keystore() -> None:
    """Manage keystore (private keys and certificates)."""
    pass


@keystore.command("list")
@click.option(
    "--store",
    "-s",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Keystore path",
)
@click.option("--password", "-p", help="Keystore password")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["jks", "pkcs12"], case_sensitive=False),
    default="pkcs12",
    help="Keystore format",
)
def keystore_list(store: Path, password: Optional[str], format: str) -> None:
    """List entries in keystore."""
    try:
        ks = KeystoreManager(path=store, password=password, format=format)
        entries = ks.list_entries()

        if not entries:
            console.print("[yellow]No entries found in keystore[/yellow]")
        else:
            formatter.print_keystore_table(entries)

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise click.Abort()


@keystore.command("export")
@click.option(
    "--store",
    "-s",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Keystore path",
)
@click.option("--alias", "-a", required=True, help="Entry alias")
@click.option(
    "--output", "-o", type=click.Path(path_type=Path), required=True, help="Output file path"
)
@click.option("--password", "-p", help="Keystore password")
@click.option("--export-password", help="Export file password")
@click.option(
    "--store-format",
    type=click.Choice(["jks", "pkcs12"], case_sensitive=False),
    default="pkcs12",
    help="Keystore format",
)
@click.option(
    "--output-format",
    type=click.Choice(["pkcs12", "pem"], case_sensitive=False),
    default="pkcs12",
    help="Output format",
)
def keystore_export(
    store: Path,
    alias: str,
    output: Path,
    password: Optional[str],
    export_password: Optional[str],
    store_format: str,
    output_format: str,
) -> None:
    """Export entry from keystore."""
    try:
        ks = KeystoreManager(path=store, password=password, format=store_format)
        ks.export_entry(alias, output, output_format, export_password)
        console.print(f"[green]✓[/green] Entry exported to {output}")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise click.Abort()


@cli.command()
@click.option(
    "--input",
    "-i",
    "input_path",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Input file",
)
@click.option(
    "--output", "-o", type=click.Path(path_type=Path), required=True, help="Output file"
)
@click.option(
    "--from",
    "from_format",
    type=click.Choice(["pem", "der", "pkcs12", "jks"], case_sensitive=False),
    required=True,
    help="Source format",
)
@click.option(
    "--to",
    "to_format",
    type=click.Choice(["pem", "der", "pkcs12", "jks"], case_sensitive=False),
    required=True,
    help="Target format",
)
@click.option("--password", "-p", help="Password (for JKS/PKCS12)")
def convert(
    input_path: Path, output: Path, from_format: str, to_format: str, password: Optional[str]
) -> None:
    """Convert certificate between formats."""
    try:
        CertificateConverter.convert(input_path, output, from_format, to_format, password)
        console.print(
            f"[green]✓[/green] Converted {from_format.upper()} to {to_format.upper()}: {output}"
        )

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise click.Abort()


@cli.command()
@click.option(
    "--cert",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Certificate file",
)
@click.option(
    "--chain",
    type=click.Path(exists=True, path_type=Path),
    multiple=True,
    help="Chain certificate files",
)
@click.option(
    "--truststore",
    "-t",
    type=click.Path(exists=True, path_type=Path),
    help="Truststore for validation",
)
@click.option("--truststore-password", help="Truststore password")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def validate(
    cert: Path,
    chain: tuple,
    truststore: Optional[Path],
    truststore_password: Optional[str],
    verbose: bool,
) -> None:
    """Validate certificate and chain."""
    try:
        # Load certificate
        with open(cert, "r") as f:
            cert_data = f.read()
        certificate = CertificateParser.parse_pem(cert_data)

        # Build chain
        cert_chain = [certificate]
        for chain_file in chain:
            with open(chain_file, "r") as f:
                chain_data = f.read()
            chain_cert = CertificateParser.parse_pem(chain_data)
            cert_chain.append(chain_cert)

        # Load truststore if provided
        trusted_certs = []
        if truststore:
            ts = TruststoreManager(path=truststore, password=truststore_password, format="jks")
            trusted_certs = [entry.certificate for entry in ts.list_certificates()]

        # Validate
        validator = CertificateValidator(truststore=trusted_certs)
        result = validator.validate_chain(cert_chain, use_truststore=bool(truststore))

        # Display results
        if result.is_valid:
            console.print("[bold green]✓ Certificate chain is valid[/bold green]")
        else:
            console.print("[bold red]✗ Certificate chain is INVALID[/bold red]")

        if verbose or not result.is_valid:
            console.print("\n[bold]Validation Details:[/bold]")
            for msg in result.messages:
                console.print(f"  • {msg}")

        # Display certificate info
        if verbose:
            console.print()
            formatter.format_certificate(certificate, verbose=True)

            if len(cert_chain) > 1:
                console.print()
                formatter.format_chain(cert_chain)

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise click.Abort()


@cli.command()
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    help="Configuration file path",
)
def tui(config: Optional[Path]) -> None:
    """Launch interactive TUI (Text User Interface)."""
    try:
        from cert_checker.tui import CertCheckerApp

        app = CertCheckerApp(config_path=config)
        app.run()

    except ImportError:
        console.print(
            "[bold red]Error:[/bold red] TUI dependencies not installed. "
            "Install with: pip install textual"
        )
        raise click.Abort()
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise click.Abort()


if __name__ == "__main__":
    cli()
