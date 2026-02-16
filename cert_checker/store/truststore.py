"""Truststore management for various formats."""

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

import jks
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import pkcs12

from cert_checker.utils.cert_parser import CertificateParser


@dataclass
class CertificateEntry:
    """Certificate entry in truststore."""

    alias: str
    certificate: x509.Certificate
    entry_type: str = "trusted_cert"


class TruststoreManager:
    """Manage truststore in various formats."""

    def __init__(
        self, path: Optional[Path] = None, password: Optional[str] = None, format: str = "jks"
    ):
        """
        Initialize truststore manager.

        Args:
            path: Path to truststore file
            password: Truststore password
            format: Truststore format (jks, pkcs12, pem)
        """
        self.path = path
        self.password = password
        self.format = format.lower()
        self.entries: Dict[str, CertificateEntry] = {}

        if path and path.exists():
            self.load()

    def load(self, path: Optional[Path] = None, password: Optional[str] = None) -> None:
        """
        Load truststore from file.

        Args:
            path: Truststore file path (uses instance path if not provided)
            password: Truststore password (uses instance password if not provided)
        """
        path = path or self.path
        password = password or self.password

        if not path or not path.exists():
            raise FileNotFoundError(f"Truststore not found: {path}")

        self.path = path
        self.password = password

        if self.format == "jks":
            self._load_jks(path, password)
        elif self.format == "pkcs12":
            self._load_pkcs12(path, password)
        elif self.format == "pem":
            self._load_pem_dir(path)
        else:
            raise ValueError(f"Unsupported format: {self.format}")

    def _load_jks(self, path: Path, password: Optional[str]) -> None:
        """Load JKS truststore."""
        # jks library expects string, not bytes
        pwd = password if password else ""

        try:
            keystore = jks.KeyStore.load(str(path), pwd)

            for alias, entry in keystore.certs.items():
                cert = x509.load_der_x509_certificate(entry.cert, default_backend())
                self.entries[alias] = CertificateEntry(
                    alias=alias, certificate=cert, entry_type="trusted_cert"
                )

        except Exception as e:
            raise RuntimeError(f"Failed to load JKS truststore: {e}")

    def _load_pkcs12(self, path: Path, password: Optional[str]) -> None:
        """Load PKCS12 truststore."""
        pwd = password.encode("utf-8") if password else None

        try:
            with open(path, "rb") as f:
                p12_data = f.read()

            private_key, certificate, ca_certs = pkcs12.load_key_and_certificates(
                p12_data, pwd, default_backend()
            )

            # Add main certificate
            if certificate:
                alias = CertificateParser.get_subject_cn(certificate) or "certificate"
                self.entries[alias] = CertificateEntry(
                    alias=alias, certificate=certificate
                )

            # Add CA certificates
            if ca_certs:
                for i, ca_cert in enumerate(ca_certs):
                    alias = CertificateParser.get_subject_cn(ca_cert) or f"ca_cert_{i}"
                    self.entries[alias] = CertificateEntry(
                        alias=alias, certificate=ca_cert
                    )

        except Exception as e:
            raise RuntimeError(f"Failed to load PKCS12 truststore: {e}")

    def _load_pem_dir(self, path: Path) -> None:
        """Load PEM certificates from directory."""
        if path.is_file():
            # Single PEM file
            with open(path, "r") as f:
                pem_data = f.read()
            cert = CertificateParser.parse_pem(pem_data)
            alias = CertificateParser.get_subject_cn(cert) or path.stem
            self.entries[alias] = CertificateEntry(alias=alias, certificate=cert)
        elif path.is_dir():
            # Directory of PEM files
            for pem_file in path.glob("*.crt"):
                with open(pem_file, "r") as f:
                    pem_data = f.read()
                cert = CertificateParser.parse_pem(pem_data)
                alias = pem_file.stem
                self.entries[alias] = CertificateEntry(alias=alias, certificate=cert)
        else:
            raise ValueError(f"Invalid PEM path: {path}")

    def list_certificates(self) -> List[CertificateEntry]:
        """
        List all certificates in truststore.

        Returns:
            List of certificate entries
        """
        return list(self.entries.values())

    def get_certificate(self, alias: str) -> Optional[x509.Certificate]:
        """
        Get certificate by alias.

        Args:
            alias: Certificate alias

        Returns:
            Certificate or None if not found
        """
        entry = self.entries.get(alias)
        return entry.certificate if entry else None

    def add_certificate(
        self, cert: x509.Certificate, alias: str, overwrite: bool = False
    ) -> bool:
        """
        Add certificate to truststore.

        Args:
            cert: Certificate to add
            alias: Certificate alias
            overwrite: Whether to overwrite existing entry

        Returns:
            True if successful

        Raises:
            ValueError: If alias exists and overwrite is False
        """
        if alias in self.entries and not overwrite:
            raise ValueError(f"Alias '{alias}' already exists")

        self.entries[alias] = CertificateEntry(alias=alias, certificate=cert)
        return True

    def remove_certificate(self, alias: str) -> bool:
        """
        Remove certificate from truststore.

        Args:
            alias: Certificate alias

        Returns:
            True if removed, False if not found
        """
        if alias in self.entries:
            del self.entries[alias]
            return True
        return False

    def export_certificate(
        self, alias: str, output_path: Path, format: str = "pem"
    ) -> bool:
        """
        Export certificate to file.

        Args:
            alias: Certificate alias
            output_path: Output file path
            format: Output format (pem, der)

        Returns:
            True if successful

        Raises:
            KeyError: If alias not found
        """
        cert = self.get_certificate(alias)
        if not cert:
            raise KeyError(f"Certificate '{alias}' not found")

        format = format.lower()

        if format == "pem":
            pem_data = CertificateParser.to_pem(cert)
            with open(output_path, "w") as f:
                f.write(pem_data)
        elif format == "der":
            der_data = CertificateParser.to_der(cert)
            with open(output_path, "wb") as f:
                f.write(der_data)
        else:
            raise ValueError(f"Unsupported export format: {format}")

        return True

    def save(
        self, path: Optional[Path] = None, password: Optional[str] = None
    ) -> bool:
        """
        Save truststore to file.

        Args:
            path: Output file path (uses instance path if not provided)
            password: Truststore password (uses instance password if not provided)

        Returns:
            True if successful
        """
        path = path or self.path
        password = password or self.password

        if not path:
            raise ValueError("No path specified for saving truststore")

        if self.format == "jks":
            return self._save_jks(path, password)
        elif self.format == "pkcs12":
            return self._save_pkcs12(path, password)
        elif self.format == "pem":
            return self._save_pem_dir(path)
        else:
            raise ValueError(f"Unsupported format: {self.format}")

    def _save_jks(self, path: Path, password: Optional[str]) -> bool:
        """Save as JKS truststore using keytool."""
        # JKS saving requires keytool - export each cert and import with keytool
        if path.exists():
            path.unlink()

        pwd = password or "changeit"

        for alias, entry in self.entries.items():
            # Export to temp PEM file
            temp_pem = Path(f"/tmp/{alias}.pem")
            pem_data = CertificateParser.to_pem(entry.certificate)
            with open(temp_pem, "w") as f:
                f.write(pem_data)

            # Import with keytool
            cmd = [
                "keytool",
                "-importcert",
                "-noprompt",
                "-alias",
                alias,
                "-file",
                str(temp_pem),
                "-keystore",
                str(path),
                "-storetype",
                "JKS",
                "-storepass",
                pwd,
            ]

            try:
                subprocess.run(cmd, check=True, capture_output=True)
            finally:
                temp_pem.unlink()

        return True

    def _save_pkcs12(self, path: Path, password: Optional[str]) -> bool:
        """Save as PKCS12 truststore."""
        pwd = password.encode("utf-8") if password else b"changeit"

        # Collect all certificates
        certs = [entry.certificate for entry in self.entries.values()]

        # Create PKCS12 with certificates only (no private key)
        p12_data = pkcs12.serialize_key_and_certificates(
            name=None,
            key=None,
            cert=certs[0] if certs else None,
            cas=certs[1:] if len(certs) > 1 else None,
            encryption_algorithm=pkcs12.NoEncryption(),
        )

        with open(path, "wb") as f:
            f.write(p12_data)

        return True

    def _save_pem_dir(self, path: Path) -> bool:
        """Save as PEM directory."""
        if not path.exists():
            path.mkdir(parents=True)

        for alias, entry in self.entries.items():
            pem_file = path / f"{alias}.crt"
            pem_data = CertificateParser.to_pem(entry.certificate)
            with open(pem_file, "w") as f:
                f.write(pem_data)

        return True

    def import_from_file(self, cert_path: Path, alias: Optional[str] = None) -> str:
        """
        Import certificate from file.

        Args:
            cert_path: Path to certificate file
            alias: Alias for certificate (uses filename if not provided)

        Returns:
            Alias used for imported certificate
        """
        # Detect format
        if cert_path.suffix.lower() in [".pem", ".crt", ".cer"]:
            with open(cert_path, "r") as f:
                pem_data = f.read()
            cert = CertificateParser.parse_pem(pem_data)
        elif cert_path.suffix.lower() == ".der":
            with open(cert_path, "rb") as f:
                der_data = f.read()
            cert = CertificateParser.parse_der(der_data)
        else:
            raise ValueError(f"Unsupported certificate format: {cert_path.suffix}")

        # Use provided alias or derive from file/cert
        if not alias:
            alias = CertificateParser.get_subject_cn(cert) or cert_path.stem

        self.add_certificate(cert, alias, overwrite=True)
        return alias
