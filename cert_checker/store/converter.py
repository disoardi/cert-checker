"""Certificate format converter."""

import subprocess
from pathlib import Path
from typing import List, Optional, Tuple

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import pkcs12

from cert_checker.utils.cert_parser import CertificateParser


class CertificateConverter:
    """Convert certificates between different formats."""

    @staticmethod
    def pem_to_der(pem_data: str) -> bytes:
        """
        Convert PEM to DER format.

        Args:
            pem_data: PEM-encoded certificate

        Returns:
            DER-encoded certificate bytes
        """
        cert = CertificateParser.parse_pem(pem_data)
        return CertificateParser.to_der(cert)

    @staticmethod
    def der_to_pem(der_data: bytes) -> str:
        """
        Convert DER to PEM format.

        Args:
            der_data: DER-encoded certificate

        Returns:
            PEM-encoded certificate string
        """
        cert = CertificateParser.parse_der(der_data)
        return CertificateParser.to_pem(cert)

    @staticmethod
    def pkcs12_to_pem(
        p12_path: Path, password: Optional[bytes] = None
    ) -> Tuple[Optional[bytes], Optional[x509.Certificate], List[x509.Certificate]]:
        """
        Extract key and certificates from PKCS12 file.

        Args:
            p12_path: Path to PKCS12 file
            password: PKCS12 password

        Returns:
            Tuple of (private_key, certificate, ca_certificates)
        """
        with open(p12_path, "rb") as f:
            p12_data = f.read()

        private_key, certificate, ca_certs = pkcs12.load_key_and_certificates(
            p12_data, password, default_backend()
        )

        return private_key, certificate, ca_certs or []

    @staticmethod
    def pem_to_pkcs12(
        key_path: Optional[Path],
        cert_path: Path,
        output_path: Path,
        password: bytes,
        ca_certs_paths: Optional[List[Path]] = None,
        friendly_name: Optional[str] = None,
    ) -> None:
        """
        Create PKCS12 file from PEM files.

        Args:
            key_path: Path to private key PEM file (optional)
            cert_path: Path to certificate PEM file
            output_path: Output PKCS12 file path
            password: PKCS12 password
            ca_certs_paths: List of CA certificate PEM files
            friendly_name: Friendly name for the entry
        """
        # Load certificate
        with open(cert_path, "rb") as f:
            cert_data = f.read()
        cert = x509.load_pem_x509_certificate(cert_data, default_backend())

        # Load private key if provided
        private_key = None
        if key_path:
            with open(key_path, "rb") as f:
                key_data = f.read()
            private_key = serialization.load_pem_private_key(
                key_data, password=None, backend=default_backend()
            )

        # Load CA certificates if provided
        ca_certs = []
        if ca_certs_paths:
            for ca_path in ca_certs_paths:
                with open(ca_path, "rb") as f:
                    ca_data = f.read()
                ca_cert = x509.load_pem_x509_certificate(ca_data, default_backend())
                ca_certs.append(ca_cert)

        # Create PKCS12
        p12_data = pkcs12.serialize_key_and_certificates(
            name=friendly_name.encode("utf-8") if friendly_name else None,
            key=private_key,
            cert=cert,
            cas=ca_certs if ca_certs else None,
            encryption_algorithm=serialization.BestAvailableEncryption(password),
        )

        # Write PKCS12 file
        with open(output_path, "wb") as f:
            f.write(p12_data)

    @staticmethod
    def jks_to_pkcs12(
        jks_path: Path,
        pkcs12_path: Path,
        password: str,
        alias: Optional[str] = None,
    ) -> bool:
        """
        Convert JKS to PKCS12 using keytool.

        Note: Requires Java keytool to be installed.

        Args:
            jks_path: Path to JKS file
            pkcs12_path: Output PKCS12 file path
            password: Keystore password (same for source and destination)
            alias: Specific alias to export (optional)

        Returns:
            True if successful

        Raises:
            FileNotFoundError: If keytool is not found
            subprocess.CalledProcessError: If conversion fails
        """
        cmd = [
            "keytool",
            "-importkeystore",
            "-srckeystore",
            str(jks_path),
            "-destkeystore",
            str(pkcs12_path),
            "-srcstoretype",
            "JKS",
            "-deststoretype",
            "PKCS12",
            "-srcstorepass",
            password,
            "-deststorepass",
            password,
        ]

        if alias:
            cmd.extend(["-srcalias", alias, "-destalias", alias])
        else:
            cmd.append("-noprompt")

        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            return True
        except FileNotFoundError:
            raise FileNotFoundError(
                "keytool not found. Please install Java JDK/JRE."
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Conversion failed: {e.stderr}")

    @staticmethod
    def pkcs12_to_jks(
        pkcs12_path: Path,
        jks_path: Path,
        password: str,
        alias: Optional[str] = None,
    ) -> bool:
        """
        Convert PKCS12 to JKS using keytool.

        Note: Requires Java keytool to be installed.

        Args:
            pkcs12_path: Path to PKCS12 file
            jks_path: Output JKS file path
            password: Keystore password (same for source and destination)
            alias: Specific alias to import (optional)

        Returns:
            True if successful

        Raises:
            FileNotFoundError: If keytool is not found
            subprocess.CalledProcessError: If conversion fails
        """
        cmd = [
            "keytool",
            "-importkeystore",
            "-srckeystore",
            str(pkcs12_path),
            "-destkeystore",
            str(jks_path),
            "-srcstoretype",
            "PKCS12",
            "-deststoretype",
            "JKS",
            "-srcstorepass",
            password,
            "-deststorepass",
            password,
        ]

        if alias:
            cmd.extend(["-srcalias", alias, "-destalias", alias])
        else:
            cmd.append("-noprompt")

        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            return True
        except FileNotFoundError:
            raise FileNotFoundError(
                "keytool not found. Please install Java JDK/JRE."
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Conversion failed: {e.stderr}")

    @staticmethod
    def convert(
        input_path: Path,
        output_path: Path,
        from_format: str,
        to_format: str,
        password: Optional[str] = None,
    ) -> bool:
        """
        Convert certificate between formats.

        Args:
            input_path: Input file path
            output_path: Output file path
            from_format: Source format (pem, der, pkcs12, jks)
            to_format: Target format (pem, der, pkcs12, jks)
            password: Password for encrypted formats

        Returns:
            True if successful

        Raises:
            ValueError: If conversion is not supported
        """
        from_format = from_format.lower()
        to_format = to_format.lower()

        # PEM to DER
        if from_format == "pem" and to_format == "der":
            with open(input_path, "r") as f:
                pem_data = f.read()
            der_data = CertificateConverter.pem_to_der(pem_data)
            with open(output_path, "wb") as f:
                f.write(der_data)
            return True

        # DER to PEM
        elif from_format == "der" and to_format == "pem":
            with open(input_path, "rb") as f:
                der_data = f.read()
            pem_data = CertificateConverter.der_to_pem(der_data)
            with open(output_path, "w") as f:
                f.write(pem_data)
            return True

        # JKS to PKCS12
        elif from_format == "jks" and to_format == "pkcs12":
            if not password:
                raise ValueError("Password required for JKS/PKCS12 conversion")
            return CertificateConverter.jks_to_pkcs12(
                input_path, output_path, password
            )

        # PKCS12 to JKS
        elif from_format == "pkcs12" and to_format == "jks":
            if not password:
                raise ValueError("Password required for PKCS12/JKS conversion")
            return CertificateConverter.pkcs12_to_jks(
                input_path, output_path, password
            )

        else:
            raise ValueError(
                f"Conversion from {from_format} to {to_format} not supported"
            )
