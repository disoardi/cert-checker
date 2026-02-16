"""Remote SSL/TLS certificate checker."""

import socket
import ssl
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional

from cryptography import x509

from cert_checker.config import Config, HostConfig
from cert_checker.utils.cert_parser import CertificateParser


class CertificateStatus(Enum):
    """Certificate status enumeration."""

    VALID = "valid"
    WARNING = "warning"
    EXPIRED = "expired"
    ERROR = "error"


@dataclass
class ExpirationInfo:
    """Certificate expiration information."""

    not_before: datetime
    not_after: datetime
    days_remaining: int
    is_expired: bool
    is_warning: bool
    status: CertificateStatus


@dataclass
class HostCheckResult:
    """Result of checking a single host."""

    host_name: str
    fqdn: str
    port: int
    status: CertificateStatus
    certificate: Optional[x509.Certificate] = None
    certificate_chain: Optional[List[x509.Certificate]] = None
    expiration: Optional[ExpirationInfo] = None
    hostname_valid: Optional[bool] = None
    error: Optional[str] = None


class RemoteCertChecker:
    """Remote certificate checker."""

    def __init__(self, timeout: int = 10):
        """Initialize checker with timeout."""
        self.timeout = timeout

    def get_certificate_chain(
        self, fqdn: str, port: int = 443, timeout: Optional[int] = None
    ) -> List[x509.Certificate]:
        """
        Get certificate chain from remote host.

        Args:
            fqdn: Fully qualified domain name
            port: Port number
            timeout: Connection timeout (uses default if not provided)

        Returns:
            List of certificates in chain (leaf first)

        Raises:
            socket.timeout: Connection timeout
            socket.error: Connection error
            ssl.SSLError: SSL/TLS error
        """
        timeout = timeout or self.timeout

        # Create SSL context
        context = ssl.create_default_context()
        # Don't verify certificate (we want to get it even if invalid)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        # Connect and get certificate chain
        with socket.create_connection((fqdn, port), timeout=timeout) as sock:
            with context.wrap_socket(sock, server_hostname=fqdn) as ssock:
                # Get DER-encoded certificate chain
                der_cert_chain = ssock.getpeercert(binary_form=True)

                # Parse certificate
                if der_cert_chain:
                    cert = CertificateParser.parse_der(der_cert_chain)
                    return [cert]

                return []

    def check_expiration(
        self, cert: x509.Certificate, warning_days: int = 30
    ) -> ExpirationInfo:
        """
        Check certificate expiration.

        Args:
            cert: Certificate to check
            warning_days: Days before expiration to trigger warning

        Returns:
            Expiration information
        """
        not_before, not_after = CertificateParser.get_validity_period(cert)
        now = datetime.now(timezone.utc)

        # Calculate days remaining
        days_remaining = (not_after - now).days

        # Determine status
        is_expired = now > not_after
        is_warning = not is_expired and days_remaining < warning_days

        if is_expired:
            status = CertificateStatus.EXPIRED
        elif is_warning:
            status = CertificateStatus.WARNING
        else:
            status = CertificateStatus.VALID

        return ExpirationInfo(
            not_before=not_before,
            not_after=not_after,
            days_remaining=days_remaining,
            is_expired=is_expired,
            is_warning=is_warning,
            status=status,
        )

    def verify_hostname(self, cert: x509.Certificate, fqdn: str) -> bool:
        """
        Verify certificate hostname matches FQDN.

        Args:
            cert: Certificate to verify
            fqdn: Expected hostname

        Returns:
            True if hostname matches
        """
        # Check Common Name
        cn = CertificateParser.get_subject_cn(cert)
        if cn and self._match_hostname(cn, fqdn):
            return True

        # Check Subject Alternative Names
        san_list = CertificateParser.get_san(cert)
        for san in san_list:
            if self._match_hostname(san, fqdn):
                return True

        return False

    def _match_hostname(self, pattern: str, hostname: str) -> bool:
        """
        Match hostname against certificate pattern (supports wildcards).

        Args:
            pattern: Pattern from certificate (may contain *)
            hostname: Hostname to check

        Returns:
            True if matches
        """
        pattern = pattern.lower()
        hostname = hostname.lower()

        # Exact match
        if pattern == hostname:
            return True

        # Wildcard match
        if pattern.startswith("*."):
            pattern_parts = pattern.split(".")
            hostname_parts = hostname.split(".")

            # Must have same number of parts
            if len(pattern_parts) != len(hostname_parts):
                return False

            # Check non-wildcard parts
            for p, h in zip(pattern_parts[1:], hostname_parts[1:]):
                if p != h:
                    return False

            return True

        return False

    def check_host(
        self,
        fqdn: str,
        port: int = 443,
        warning_days: int = 30,
        host_name: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> HostCheckResult:
        """
        Check certificate for a single host.

        Args:
            fqdn: Fully qualified domain name
            port: Port number
            warning_days: Days before expiration to trigger warning
            host_name: Friendly name for host
            timeout: Connection timeout

        Returns:
            Check result
        """
        host_name = host_name or fqdn

        try:
            # Get certificate chain
            cert_chain = self.get_certificate_chain(fqdn, port, timeout)

            if not cert_chain:
                return HostCheckResult(
                    host_name=host_name,
                    fqdn=fqdn,
                    port=port,
                    status=CertificateStatus.ERROR,
                    error="No certificate received",
                )

            # Check leaf certificate
            cert = cert_chain[0]

            # Check expiration
            expiration = self.check_expiration(cert, warning_days)

            # Verify hostname
            hostname_valid = self.verify_hostname(cert, fqdn)

            # Determine overall status
            status = expiration.status
            if not hostname_valid:
                status = CertificateStatus.ERROR

            return HostCheckResult(
                host_name=host_name,
                fqdn=fqdn,
                port=port,
                status=status,
                certificate=cert,
                certificate_chain=cert_chain,
                expiration=expiration,
                hostname_valid=hostname_valid,
            )

        except socket.timeout:
            return HostCheckResult(
                host_name=host_name,
                fqdn=fqdn,
                port=port,
                status=CertificateStatus.ERROR,
                error=f"Connection timeout after {timeout or self.timeout}s",
            )
        except socket.gaierror as e:
            return HostCheckResult(
                host_name=host_name,
                fqdn=fqdn,
                port=port,
                status=CertificateStatus.ERROR,
                error=f"DNS resolution failed: {e}",
            )
        except (socket.error, ssl.SSLError) as e:
            return HostCheckResult(
                host_name=host_name,
                fqdn=fqdn,
                port=port,
                status=CertificateStatus.ERROR,
                error=f"Connection error: {e}",
            )
        except Exception as e:
            return HostCheckResult(
                host_name=host_name,
                fqdn=fqdn,
                port=port,
                status=CertificateStatus.ERROR,
                error=f"Unexpected error: {e}",
            )

    def check_all_hosts(self, config: Config) -> List[HostCheckResult]:
        """
        Check all enabled hosts from configuration.

        Args:
            config: Configuration with hosts to check

        Returns:
            List of check results
        """
        results = []
        enabled_hosts = config.get_enabled_hosts()

        for host_config in enabled_hosts:
            result = self.check_host(
                fqdn=host_config.fqdn,
                port=host_config.port,
                warning_days=host_config.warning_days,
                host_name=host_config.name,
                timeout=config.settings.timeout,
            )
            results.append(result)

        return results

    def check_host_config(self, host_config: HostConfig, timeout: int = 10) -> HostCheckResult:
        """
        Check a single host from configuration.

        Args:
            host_config: Host configuration
            timeout: Connection timeout

        Returns:
            Check result
        """
        return self.check_host(
            fqdn=host_config.fqdn,
            port=host_config.port,
            warning_days=host_config.warning_days,
            host_name=host_config.name,
            timeout=timeout,
        )
