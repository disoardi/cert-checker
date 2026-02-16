"""Keystore management for private keys and certificates."""

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

import jks
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import pkcs12

from cert_checker.utils.cert_parser import CertificateParser


@dataclass
class KeyEntry:
    """Key entry in keystore."""

    alias: str
    certificate: x509.Certificate
    certificate_chain: List[x509.Certificate]
    has_private_key: bool = True


class KeystoreManager:
    """Manage keystore with private keys and certificates."""

    def __init__(
        self,
        path: Optional[Path] = None,
        password: Optional[str] = None,
        format: str = "pkcs12",
    ):
        """
        Initialize keystore manager.

        Args:
            path: Path to keystore file
            password: Keystore password
            format: Keystore format (jks, pkcs12)
        """
        self.path = path
        self.password = password
        self.format = format.lower()
        self.entries: Dict[str, KeyEntry] = {}
        self._private_keys: Dict[str, bytes] = {}

        if path and path.exists():
            self.load()

    def load(self, path: Optional[Path] = None, password: Optional[str] = None) -> None:
        """
        Load keystore from file.

        Args:
            path: Keystore file path
            password: Keystore password
        """
        path = path or self.path
        password = password or self.password

        if not path or not path.exists():
            raise FileNotFoundError(f"Keystore not found: {path}")

        self.path = path
        self.password = password

        if self.format == "jks":
            self._load_jks(path, password)
        elif self.format == "pkcs12":
            self._load_pkcs12(path, password)
        else:
            raise ValueError(f"Unsupported format: {self.format}")

    def _load_jks(self, path: Path, password: Optional[str]) -> None:
        """Load JKS keystore."""
        pwd = password.encode("utf-8") if password else b""

        try:
            keystore = jks.KeyStore.load(str(path), pwd)

            # Load private key entries
            for alias, entry in keystore.private_keys.items():
                # Get certificate chain
                cert_chain = []
                for cert_data in entry.cert_chain:
                    cert = x509.load_der_x509_certificate(cert_data[1], default_backend())
                    cert_chain.append(cert)

                if cert_chain:
                    self.entries[alias] = KeyEntry(
                        alias=alias,
                        certificate=cert_chain[0],
                        certificate_chain=cert_chain,
                        has_private_key=True,
                    )

                    # Store encrypted private key
                    self._private_keys[alias] = entry.pkey_pkcs8

        except Exception as e:
            raise RuntimeError(f"Failed to load JKS keystore: {e}")

    def _load_pkcs12(self, path: Path, password: Optional[str]) -> None:
        """Load PKCS12 keystore."""
        pwd = password.encode("utf-8") if password else None

        try:
            with open(path, "rb") as f:
                p12_data = f.read()

            private_key, certificate, ca_certs = pkcs12.load_key_and_certificates(
                p12_data, pwd, default_backend()
            )

            if certificate and private_key:
                # Build certificate chain
                cert_chain = [certificate]
                if ca_certs:
                    cert_chain.extend(ca_certs)

                alias = CertificateParser.get_subject_cn(certificate) or "key"

                self.entries[alias] = KeyEntry(
                    alias=alias,
                    certificate=certificate,
                    certificate_chain=cert_chain,
                    has_private_key=True,
                )

                # Store private key in PEM format
                pkey_pem = private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption(),
                )
                self._private_keys[alias] = pkey_pem

        except Exception as e:
            raise RuntimeError(f"Failed to load PKCS12 keystore: {e}")

    def list_entries(self) -> List[KeyEntry]:
        """
        List all key entries in keystore.

        Returns:
            List of key entries
        """
        return list(self.entries.values())

    def get_certificate(self, alias: str) -> Optional[x509.Certificate]:
        """
        Get certificate by alias.

        Args:
            alias: Entry alias

        Returns:
            Certificate or None
        """
        entry = self.entries.get(alias)
        return entry.certificate if entry else None

    def get_certificate_chain(self, alias: str) -> Optional[List[x509.Certificate]]:
        """
        Get certificate chain by alias.

        Args:
            alias: Entry alias

        Returns:
            Certificate chain or None
        """
        entry = self.entries.get(alias)
        return entry.certificate_chain if entry else None

    def has_private_key(self, alias: str) -> bool:
        """
        Check if entry has private key.

        Args:
            alias: Entry alias

        Returns:
            True if has private key
        """
        return alias in self._private_keys

    def add_key_entry(
        self,
        alias: str,
        private_key_path: Path,
        cert_path: Path,
        chain_paths: Optional[List[Path]] = None,
        key_password: Optional[str] = None,
        overwrite: bool = False,
    ) -> bool:
        """
        Add key entry to keystore.

        Args:
            alias: Entry alias
            private_key_path: Path to private key file
            cert_path: Path to certificate file
            chain_paths: Paths to chain certificates
            key_password: Private key password
            overwrite: Whether to overwrite existing entry

        Returns:
            True if successful
        """
        if alias in self.entries and not overwrite:
            raise ValueError(f"Alias '{alias}' already exists")

        # Load private key
        with open(private_key_path, "rb") as f:
            key_data = f.read()

        key_pwd = key_password.encode("utf-8") if key_password else None
        private_key = serialization.load_pem_private_key(
            key_data, password=key_pwd, backend=default_backend()
        )

        # Load certificate
        with open(cert_path, "rb") as f:
            cert_data = f.read()
        certificate = CertificateParser.parse_pem(cert_data.decode("utf-8"))

        # Load chain certificates
        cert_chain = [certificate]
        if chain_paths:
            for chain_path in chain_paths:
                with open(chain_path, "rb") as f:
                    chain_data = f.read()
                chain_cert = CertificateParser.parse_pem(chain_data.decode("utf-8"))
                cert_chain.append(chain_cert)

        # Store entry
        self.entries[alias] = KeyEntry(
            alias=alias,
            certificate=certificate,
            certificate_chain=cert_chain,
            has_private_key=True,
        )

        # Store private key
        pkey_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
        self._private_keys[alias] = pkey_pem

        return True

    def remove_entry(self, alias: str) -> bool:
        """
        Remove entry from keystore.

        Args:
            alias: Entry alias

        Returns:
            True if removed
        """
        if alias in self.entries:
            del self.entries[alias]
            if alias in self._private_keys:
                del self._private_keys[alias]
            return True
        return False

    def export_entry(
        self, alias: str, output_path: Path, format: str = "pkcs12", password: Optional[str] = None
    ) -> bool:
        """
        Export key entry to file.

        Args:
            alias: Entry alias
            output_path: Output file path
            format: Export format (pkcs12, pem)
            password: Export password

        Returns:
            True if successful
        """
        entry = self.entries.get(alias)
        if not entry:
            raise KeyError(f"Entry '{alias}' not found")

        if alias not in self._private_keys:
            raise ValueError(f"No private key for alias '{alias}'")

        format = format.lower()

        if format == "pkcs12":
            # Load private key
            private_key = serialization.load_pem_private_key(
                self._private_keys[alias], password=None, backend=default_backend()
            )

            # Create PKCS12
            pwd = password.encode("utf-8") if password else b"changeit"
            p12_data = pkcs12.serialize_key_and_certificates(
                name=alias.encode("utf-8"),
                key=private_key,
                cert=entry.certificate,
                cas=entry.certificate_chain[1:] if len(entry.certificate_chain) > 1 else None,
                encryption_algorithm=serialization.BestAvailableEncryption(pwd),
            )

            with open(output_path, "wb") as f:
                f.write(p12_data)

        elif format == "pem":
            # Export as separate PEM files
            base_path = output_path.parent / output_path.stem

            # Private key
            key_path = Path(f"{base_path}_key.pem")
            with open(key_path, "wb") as f:
                f.write(self._private_keys[alias])

            # Certificate
            cert_path = Path(f"{base_path}_cert.pem")
            with open(cert_path, "w") as f:
                f.write(CertificateParser.to_pem(entry.certificate))

            # Chain
            if len(entry.certificate_chain) > 1:
                chain_path = Path(f"{base_path}_chain.pem")
                with open(chain_path, "w") as f:
                    for cert in entry.certificate_chain[1:]:
                        f.write(CertificateParser.to_pem(cert))

        else:
            raise ValueError(f"Unsupported export format: {format}")

        return True

    def save(self, path: Optional[Path] = None, password: Optional[str] = None) -> bool:
        """
        Save keystore to file.

        Args:
            path: Output file path
            password: Keystore password

        Returns:
            True if successful
        """
        path = path or self.path
        password = password or self.password

        if not path:
            raise ValueError("No path specified for saving keystore")

        if self.format == "pkcs12":
            return self._save_pkcs12(path, password)
        elif self.format == "jks":
            return self._save_jks(path, password)
        else:
            raise ValueError(f"Unsupported format: {self.format}")

    def _save_pkcs12(self, path: Path, password: Optional[str]) -> bool:
        """Save as PKCS12 keystore."""
        if not self.entries:
            raise ValueError("No entries to save")

        # Get first entry (PKCS12 typically holds one key)
        alias = next(iter(self.entries))
        entry = self.entries[alias]

        if alias not in self._private_keys:
            raise ValueError("No private key found")

        # Load private key
        private_key = serialization.load_pem_private_key(
            self._private_keys[alias], password=None, backend=default_backend()
        )

        # Create PKCS12
        pwd = password.encode("utf-8") if password else b"changeit"
        p12_data = pkcs12.serialize_key_and_certificates(
            name=alias.encode("utf-8"),
            key=private_key,
            cert=entry.certificate,
            cas=entry.certificate_chain[1:] if len(entry.certificate_chain) > 1 else None,
            encryption_algorithm=serialization.BestAvailableEncryption(pwd),
        )

        with open(path, "wb") as f:
            f.write(p12_data)

        return True

    def _save_jks(self, path: Path, password: Optional[str]) -> bool:
        """Save as JKS keystore using keytool."""
        # Export to PKCS12 first, then convert
        temp_p12 = Path("/tmp/temp_keystore.p12")
        self._save_pkcs12(temp_p12, password)

        pwd = password or "changeit"

        try:
            cmd = [
                "keytool",
                "-importkeystore",
                "-srckeystore",
                str(temp_p12),
                "-destkeystore",
                str(path),
                "-srcstoretype",
                "PKCS12",
                "-deststoretype",
                "JKS",
                "-srcstorepass",
                pwd,
                "-deststorepass",
                pwd,
                "-noprompt",
            ]

            subprocess.run(cmd, check=True, capture_output=True)
            return True

        finally:
            if temp_p12.exists():
                temp_p12.unlink()
