"""Display and formatting utilities using Rich."""

import json
from datetime import datetime
from typing import List, Optional

from cryptography import x509
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree
from rich import box

from cert_checker.checker.remote import CertificateStatus, HostCheckResult
from cert_checker.store.truststore import CertificateEntry
from cert_checker.store.keystore import KeyEntry
from cert_checker.utils.cert_parser import CertificateParser


class DisplayFormatter:
    """Format output using Rich library."""

    def __init__(self, console: Optional[Console] = None):
        """Initialize formatter with console."""
        self.console = console or Console()

    def _get_status_style(self, status: CertificateStatus) -> str:
        """Get Rich style for status."""
        if status == CertificateStatus.VALID:
            return "bold green"
        elif status == CertificateStatus.WARNING:
            return "bold yellow"
        elif status == CertificateStatus.EXPIRED:
            return "bold red"
        else:
            return "bold red"

    def _get_status_icon(self, status: CertificateStatus) -> str:
        """Get icon for status."""
        if status == CertificateStatus.VALID:
            return "✓"
        elif status == CertificateStatus.WARNING:
            return "⚠"
        elif status == CertificateStatus.EXPIRED:
            return "✗"
        else:
            return "✗"

    def format_check_result(self, result: HostCheckResult, verbose: bool = False) -> None:
        """
        Format and print single host check result.

        Args:
            result: Host check result
            verbose: Show detailed information
        """
        status_style = self._get_status_style(result.status)
        icon = self._get_status_icon(result.status)

        # Create title
        title = f"{icon} {result.host_name} ({result.fqdn}:{result.port})"

        # Create content
        if result.error:
            content = f"[bold red]Error:[/bold red] {result.error}"
            panel = Panel(content, title=title, border_style="red")
        else:
            content_lines = []

            if result.certificate and result.expiration:
                content_lines.append(
                    f"[bold]Subject:[/bold] {CertificateParser.get_subject_cn(result.certificate)}"
                )
                content_lines.append(
                    f"[bold]Issuer:[/bold] {CertificateParser.get_issuer_cn(result.certificate)}"
                )
                content_lines.append(
                    f"[bold]Valid Until:[/bold] {result.expiration.not_after.strftime('%Y-%m-%d %H:%M:%S UTC')}"
                )

                days_style = "green" if result.expiration.days_remaining > 30 else "yellow"
                if result.expiration.is_expired:
                    days_style = "red"
                    days_text = f"{abs(result.expiration.days_remaining)} days ago"
                else:
                    days_text = f"{result.expiration.days_remaining} days"

                content_lines.append(
                    f"[bold]Days Remaining:[/bold] [{days_style}]{days_text}[/{days_style}]"
                )

                if result.hostname_valid is not None:
                    hostname_status = "✓ Valid" if result.hostname_valid else "✗ Invalid"
                    hostname_style = "green" if result.hostname_valid else "red"
                    content_lines.append(
                        f"[bold]Hostname:[/bold] [{hostname_style}]{hostname_status}[/{hostname_style}]"
                    )

                if verbose and result.certificate:
                    san_list = CertificateParser.get_san(result.certificate)
                    if san_list:
                        content_lines.append(f"[bold]SAN:[/bold] {', '.join(san_list)}")

                    fingerprint = CertificateParser.get_fingerprint(result.certificate)
                    content_lines.append(f"[bold]Fingerprint:[/bold] {fingerprint}")

            content = "\n".join(content_lines)
            panel = Panel(content, title=title, border_style=status_style.split()[1])

        self.console.print(panel)

    def create_summary_table(self, results: List[HostCheckResult]) -> Table:
        """
        Create summary table of host check results.

        Args:
            results: List of host check results

        Returns:
            Rich Table
        """
        table = Table(title="Certificate Check Summary", box=box.ROUNDED)

        table.add_column("Host", style="cyan", no_wrap=True)
        table.add_column("FQDN:Port", style="white")
        table.add_column("Status", justify="center")
        table.add_column("Expiry", justify="center")
        table.add_column("Days Left", justify="right")

        for result in results:
            icon = self._get_status_icon(result.status)
            status_style = self._get_status_style(result.status)

            if result.error:
                table.add_row(
                    result.host_name,
                    f"{result.fqdn}:{result.port}",
                    f"[{status_style}]{icon} Error[/{status_style}]",
                    "-",
                    "-",
                )
            elif result.expiration:
                expiry_date = result.expiration.not_after.strftime("%Y-%m-%d")
                days = result.expiration.days_remaining

                if result.expiration.is_expired:
                    days_text = f"[red]-{abs(days)}[/red]"
                elif result.expiration.is_warning:
                    days_text = f"[yellow]{days}[/yellow]"
                else:
                    days_text = f"[green]{days}[/green]"

                table.add_row(
                    result.host_name,
                    f"{result.fqdn}:{result.port}",
                    f"[{status_style}]{icon} {result.status.value.title()}[/{status_style}]",
                    expiry_date,
                    days_text,
                )

        return table

    def print_summary_table(self, results: List[HostCheckResult]) -> None:
        """Print summary table."""
        table = self.create_summary_table(results)
        self.console.print(table)

    def format_certificate(self, cert: x509.Certificate, verbose: bool = False) -> None:
        """
        Format and print certificate details.

        Args:
            cert: Certificate to display
            verbose: Show detailed information
        """
        info = CertificateParser.get_all_info(cert)

        tree = Tree(f"[bold cyan]Certificate Details[/bold cyan]")

        tree.add(f"[bold]Subject:[/bold] {info['subject_cn'] or info['subject']}")
        tree.add(f"[bold]Issuer:[/bold] {info['issuer_cn'] or info['issuer']}")

        validity = tree.add("[bold]Validity[/bold]")
        validity.add(f"Not Before: {info['not_before']}")
        validity.add(f"Not After: {info['not_after']}")

        if info['san']:
            san_node = tree.add(f"[bold]Subject Alternative Names ({len(info['san'])})[/bold]")
            for san in info['san']:
                san_node.add(san)

        tree.add(f"[bold]Serial Number:[/bold] {info['serial_number']}")
        tree.add(f"[bold]Signature Algorithm:[/bold] {info['signature_algorithm']}")

        pub_key = info['public_key']
        key_info = f"{pub_key['type']}"
        if 'size' in pub_key:
            key_info += f" ({pub_key['size']} bits)"
        if 'curve' in pub_key:
            key_info += f" ({pub_key['curve']})"
        tree.add(f"[bold]Public Key:[/bold] {key_info}")

        if verbose:
            tree.add(f"[bold]Version:[/bold] {info['version']}")
            tree.add(f"[bold]Self-Signed:[/bold] {info['is_self_signed']}")
            tree.add(f"[bold]Is CA:[/bold] {info['is_ca']}")

            if info['key_usage']:
                ku_node = tree.add("[bold]Key Usage[/bold]")
                for usage in info['key_usage']:
                    ku_node.add(usage)

            if info['extended_key_usage']:
                eku_node = tree.add("[bold]Extended Key Usage[/bold]")
                for usage in info['extended_key_usage']:
                    eku_node.add(usage)

            tree.add(f"[bold]SHA-256 Fingerprint:[/bold] {info['fingerprint_sha256']}")
            tree.add(f"[bold]SHA-1 Fingerprint:[/bold] {info['fingerprint_sha1']}")

        self.console.print(tree)

    def format_chain(self, chain: List[x509.Certificate]) -> None:
        """
        Format and print certificate chain.

        Args:
            chain: Certificate chain (leaf first)
        """
        tree = Tree("[bold cyan]Certificate Chain[/bold cyan]")

        for i, cert in enumerate(chain):
            level = "Leaf" if i == 0 else f"Intermediate {i}" if i < len(chain) - 1 else "Root"
            cn = CertificateParser.get_subject_cn(cert) or "Unknown"
            node = tree.add(f"[bold]{level}:[/bold] {cn}")

            issuer_cn = CertificateParser.get_issuer_cn(cert)
            node.add(f"Issued by: {issuer_cn}")

            not_before, not_after = CertificateParser.get_validity_period(cert)
            node.add(f"Valid until: {not_after.strftime('%Y-%m-%d')}")

        self.console.print(tree)

    def create_truststore_table(self, entries: List[CertificateEntry]) -> Table:
        """
        Create table of truststore entries.

        Args:
            entries: List of certificate entries

        Returns:
            Rich Table
        """
        table = Table(title="Truststore Certificates", box=box.ROUNDED)

        table.add_column("Alias", style="cyan")
        table.add_column("Subject CN", style="white")
        table.add_column("Issuer CN", style="white")
        table.add_column("Valid Until", justify="center")
        table.add_column("Type", justify="center")

        for entry in entries:
            subject_cn = CertificateParser.get_subject_cn(entry.certificate) or "N/A"
            issuer_cn = CertificateParser.get_issuer_cn(entry.certificate) or "N/A"
            not_before, not_after = CertificateParser.get_validity_period(entry.certificate)

            # Check if expired
            now = datetime.now(not_after.tzinfo)
            is_expired = now > not_after
            expiry_style = "red" if is_expired else "green"
            expiry_text = f"[{expiry_style}]{not_after.strftime('%Y-%m-%d')}[/{expiry_style}]"

            cert_type = "CA" if CertificateParser.is_ca(entry.certificate) else "Cert"

            table.add_row(entry.alias, subject_cn, issuer_cn, expiry_text, cert_type)

        return table

    def print_truststore_table(self, entries: List[CertificateEntry]) -> None:
        """Print truststore table."""
        table = self.create_truststore_table(entries)
        self.console.print(table)

    def create_keystore_table(self, entries: List[KeyEntry]) -> Table:
        """
        Create table of keystore entries.

        Args:
            entries: List of key entries

        Returns:
            Rich Table
        """
        table = Table(title="Keystore Entries", box=box.ROUNDED)

        table.add_column("Alias", style="cyan")
        table.add_column("Subject CN", style="white")
        table.add_column("Valid Until", justify="center")
        table.add_column("Chain Length", justify="center")
        table.add_column("Has Key", justify="center")

        for entry in entries:
            subject_cn = CertificateParser.get_subject_cn(entry.certificate) or "N/A"
            not_before, not_after = CertificateParser.get_validity_period(entry.certificate)

            # Check if expired
            now = datetime.now(not_after.tzinfo)
            is_expired = now > not_after
            expiry_style = "red" if is_expired else "green"
            expiry_text = f"[{expiry_style}]{not_after.strftime('%Y-%m-%d')}[/{expiry_style}]"

            chain_len = len(entry.certificate_chain)
            has_key = "✓" if entry.has_private_key else "✗"
            key_style = "green" if entry.has_private_key else "red"

            table.add_row(
                entry.alias,
                subject_cn,
                expiry_text,
                str(chain_len),
                f"[{key_style}]{has_key}[/{key_style}]",
            )

        return table

    def print_keystore_table(self, entries: List[KeyEntry]) -> None:
        """Print keystore table."""
        table = self.create_keystore_table(entries)
        self.console.print(table)

    def export_json(self, results: List[HostCheckResult]) -> str:
        """
        Export results to JSON.

        Args:
            results: List of host check results

        Returns:
            JSON string
        """
        data = []
        for result in results:
            entry = {
                "host_name": result.host_name,
                "fqdn": result.fqdn,
                "port": result.port,
                "status": result.status.value,
            }

            if result.error:
                entry["error"] = result.error
            elif result.certificate and result.expiration:
                entry["certificate"] = {
                    "subject_cn": CertificateParser.get_subject_cn(result.certificate),
                    "issuer_cn": CertificateParser.get_issuer_cn(result.certificate),
                    "not_before": result.expiration.not_before.isoformat(),
                    "not_after": result.expiration.not_after.isoformat(),
                    "days_remaining": result.expiration.days_remaining,
                    "is_expired": result.expiration.is_expired,
                    "fingerprint": CertificateParser.get_fingerprint(result.certificate),
                }

                if result.hostname_valid is not None:
                    entry["hostname_valid"] = result.hostname_valid

            data.append(entry)

        return json.dumps(data, indent=2)

    def export_csv(self, results: List[HostCheckResult]) -> str:
        """
        Export results to CSV.

        Args:
            results: List of host check results

        Returns:
            CSV string
        """
        lines = ["Host,FQDN,Port,Status,Subject,Issuer,Expiry,Days Remaining,Error"]

        for result in results:
            if result.error:
                lines.append(
                    f"{result.host_name},{result.fqdn},{result.port},"
                    f"{result.status.value},,,,{result.error}"
                )
            elif result.certificate and result.expiration:
                subject_cn = CertificateParser.get_subject_cn(result.certificate) or ""
                issuer_cn = CertificateParser.get_issuer_cn(result.certificate) or ""
                expiry = result.expiration.not_after.strftime("%Y-%m-%d")
                days = result.expiration.days_remaining

                lines.append(
                    f"{result.host_name},{result.fqdn},{result.port},"
                    f"{result.status.value},{subject_cn},{issuer_cn},"
                    f"{expiry},{days},"
                )

        return "\n".join(lines)
