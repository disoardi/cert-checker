"""Text User Interface using Textual."""

from pathlib import Path
from typing import Optional

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, DataTable, Footer, Header, Static, TabbedContent, TabPane
from textual.reactive import reactive

from cert_checker.checker.remote import CertificateStatus, RemoteCertChecker
from cert_checker.config import Config
from cert_checker.utils.cert_parser import CertificateParser


class CertCheckerApp(App):
    """TUI application for cert-checker."""

    CSS = """
    Screen {
        background: $surface;
    }

    #status_table {
        height: 1fr;
        border: solid $primary;
    }

    #details {
        height: 1fr;
        border: solid $primary;
        padding: 1;
    }

    .status_valid {
        color: $success;
    }

    .status_warning {
        color: $warning;
    }

    .status_expired {
        color: $error;
    }

    .status_error {
        color: $error;
    }

    Button {
        margin: 1;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh"),
        ("d", "toggle_dark", "Toggle Dark Mode"),
    ]

    config_path: Optional[Path] = None
    config: Optional[Config] = None
    selected_row: reactive[Optional[int]] = reactive(None)

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize TUI app."""
        super().__init__()
        self.config_path = config_path
        self.checker = RemoteCertChecker()
        self.results = []

    def compose(self) -> ComposeResult:
        """Compose TUI layout."""
        yield Header()

        with TabbedContent():
            with TabPane("Remote Hosts", id="tab_hosts"):
                with Vertical():
                    yield DataTable(id="status_table")
                    with Horizontal():
                        yield Button("Refresh", id="btn_refresh", variant="primary")
                        yield Button("Check Now", id="btn_check", variant="success")

            with TabPane("Details", id="tab_details"):
                yield Static("Select a host to view details", id="details")

        yield Footer()

    def on_mount(self) -> None:
        """Initialize on mount."""
        table = self.query_one("#status_table", DataTable)
        table.add_columns("Host", "FQDN:Port", "Status", "Expiry", "Days Left")
        table.cursor_type = "row"

        # Load configuration if provided
        if self.config_path:
            try:
                self.config = Config.from_file(self.config_path)
                self.refresh_data()
            except Exception as e:
                self.notify(f"Error loading config: {e}", severity="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "btn_refresh" or event.button.id == "btn_check":
            self.refresh_data()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection."""
        self.selected_row = event.row_key.value
        self.update_details()

    def refresh_data(self) -> None:
        """Refresh certificate data."""
        if not self.config:
            self.notify("No configuration loaded", severity="warning")
            return

        self.notify("Checking certificates...", severity="information")

        try:
            self.results = self.checker.check_all_hosts(self.config)
            self.update_table()
            self.notify(f"Checked {len(self.results)} hosts", severity="information")
        except Exception as e:
            self.notify(f"Error checking hosts: {e}", severity="error")

    def update_table(self) -> None:
        """Update status table with results."""
        table = self.query_one("#status_table", DataTable)
        table.clear()

        for i, result in enumerate(self.results):
            status_class = f"status_{result.status.value}"

            if result.error:
                table.add_row(
                    result.host_name,
                    f"{result.fqdn}:{result.port}",
                    f"✗ Error",
                    "-",
                    "-",
                    key=str(i),
                )
            elif result.expiration:
                icon = self._get_status_icon(result.status)
                status_text = f"{icon} {result.status.value.title()}"

                expiry_date = result.expiration.not_after.strftime("%Y-%m-%d")
                days = result.expiration.days_remaining

                if result.expiration.is_expired:
                    days_text = f"-{abs(days)}"
                else:
                    days_text = str(days)

                table.add_row(
                    result.host_name,
                    f"{result.fqdn}:{result.port}",
                    status_text,
                    expiry_date,
                    days_text,
                    key=str(i),
                )

    def update_details(self) -> None:
        """Update details panel with selected host info."""
        if self.selected_row is None or self.selected_row >= len(self.results):
            return

        result = self.results[self.selected_row]
        details = self.query_one("#details", Static)

        if result.error:
            content = f"[bold red]Error:[/bold red] {result.error}"
        elif result.certificate and result.expiration:
            subject_cn = CertificateParser.get_subject_cn(result.certificate)
            issuer_cn = CertificateParser.get_issuer_cn(result.certificate)
            san_list = CertificateParser.get_san(result.certificate)
            fingerprint = CertificateParser.get_fingerprint(result.certificate)

            lines = [
                f"[bold]Host:[/bold] {result.host_name}",
                f"[bold]FQDN:[/bold] {result.fqdn}:{result.port}",
                "",
                f"[bold]Subject CN:[/bold] {subject_cn}",
                f"[bold]Issuer CN:[/bold] {issuer_cn}",
                "",
                f"[bold]Valid From:[/bold] {result.expiration.not_before.strftime('%Y-%m-%d %H:%M:%S UTC')}",
                f"[bold]Valid Until:[/bold] {result.expiration.not_after.strftime('%Y-%m-%d %H:%M:%S UTC')}",
                f"[bold]Days Remaining:[/bold] {result.expiration.days_remaining}",
                "",
            ]

            if san_list:
                lines.append(f"[bold]SAN:[/bold] {', '.join(san_list)}")
                lines.append("")

            if result.hostname_valid is not None:
                hostname_status = "✓ Valid" if result.hostname_valid else "✗ Invalid"
                lines.append(f"[bold]Hostname Match:[/bold] {hostname_status}")

            lines.append(f"[bold]Fingerprint (SHA-256):[/bold]")
            lines.append(f"  {fingerprint}")

            content = "\n".join(lines)
        else:
            content = "No certificate data available"

        details.update(content)

    def _get_status_icon(self, status: CertificateStatus) -> str:
        """Get status icon."""
        if status == CertificateStatus.VALID:
            return "✓"
        elif status == CertificateStatus.WARNING:
            return "⚠"
        elif status == CertificateStatus.EXPIRED:
            return "✗"
        else:
            return "✗"

    def action_refresh(self) -> None:
        """Refresh action."""
        self.refresh_data()

    def action_toggle_dark(self) -> None:
        """Toggle dark mode."""
        self.dark = not self.dark


if __name__ == "__main__":
    app = CertCheckerApp()
    app.run()
