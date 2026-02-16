"""Certificate parsing and information extraction utilities."""

import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.x509.oid import ExtensionOID, NameOID


class CertificateParser:
    """Parse and extract information from X.509 certificates."""

    @staticmethod
    def parse_pem(pem_data: Union[str, bytes]) -> x509.Certificate:
        """Parse PEM-encoded certificate."""
        if isinstance(pem_data, str):
            pem_data = pem_data.encode("utf-8")
        return x509.load_pem_x509_certificate(pem_data, default_backend())

    @staticmethod
    def parse_der(der_data: bytes) -> x509.Certificate:
        """Parse DER-encoded certificate."""
        return x509.load_der_x509_certificate(der_data, default_backend())

    @staticmethod
    def parse(cert_data: Union[str, bytes], format: str = "pem") -> x509.Certificate:
        """Parse certificate in specified format."""
        if format.lower() == "pem":
            return CertificateParser.parse_pem(cert_data)
        elif format.lower() == "der":
            if isinstance(cert_data, str):
                raise ValueError("DER format requires bytes data")
            return CertificateParser.parse_der(cert_data)
        else:
            raise ValueError(f"Unsupported format: {format}")

    @staticmethod
    def get_subject(cert: x509.Certificate) -> str:
        """Get certificate subject as string."""
        return cert.subject.rfc4514_string()

    @staticmethod
    def get_subject_cn(cert: x509.Certificate) -> Optional[str]:
        """Get Common Name from subject."""
        try:
            cn_list = cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)
            if cn_list:
                return cn_list[0].value
        except Exception:
            pass
        return None

    @staticmethod
    def get_issuer(cert: x509.Certificate) -> str:
        """Get certificate issuer as string."""
        return cert.issuer.rfc4514_string()

    @staticmethod
    def get_issuer_cn(cert: x509.Certificate) -> Optional[str]:
        """Get Common Name from issuer."""
        try:
            cn_list = cert.issuer.get_attributes_for_oid(NameOID.COMMON_NAME)
            if cn_list:
                return cn_list[0].value
        except Exception:
            pass
        return None

    @staticmethod
    def get_san(cert: x509.Certificate) -> List[str]:
        """Get Subject Alternative Names."""
        try:
            san_ext = cert.extensions.get_extension_for_oid(
                ExtensionOID.SUBJECT_ALTERNATIVE_NAME
            )
            san_list = san_ext.value.get_values_for_type(x509.DNSName)
            return list(san_list)
        except x509.ExtensionNotFound:
            return []

    @staticmethod
    def get_validity_period(cert: x509.Certificate) -> Tuple[datetime, datetime]:
        """Get certificate validity period (not_before, not_after)."""
        return (cert.not_valid_before_utc, cert.not_valid_after_utc)

    @staticmethod
    def get_fingerprint(
        cert: x509.Certificate, algorithm: str = "sha256"
    ) -> str:
        """Get certificate fingerprint."""
        cert_bytes = cert.public_bytes(serialization.Encoding.DER)

        if algorithm.lower() == "sha256":
            digest = hashlib.sha256(cert_bytes).hexdigest()
        elif algorithm.lower() == "sha1":
            digest = hashlib.sha1(cert_bytes).hexdigest()
        elif algorithm.lower() == "md5":
            digest = hashlib.md5(cert_bytes).hexdigest()
        else:
            raise ValueError(f"Unsupported hash algorithm: {algorithm}")

        # Format as colon-separated pairs
        return ":".join(digest[i : i + 2] for i in range(0, len(digest), 2)).upper()

    @staticmethod
    def get_public_key_info(cert: x509.Certificate) -> Dict[str, Union[str, int]]:
        """Get public key information."""
        public_key = cert.public_key()
        key_type = type(public_key).__name__

        info: Dict[str, Union[str, int]] = {"type": key_type}

        try:
            if hasattr(public_key, "key_size"):
                info["size"] = public_key.key_size
            if hasattr(public_key, "curve"):
                info["curve"] = public_key.curve.name
        except Exception:
            pass

        return info

    @staticmethod
    def get_serial_number(cert: x509.Certificate) -> str:
        """Get certificate serial number as hex string."""
        return format(cert.serial_number, "X")

    @staticmethod
    def get_version(cert: x509.Certificate) -> int:
        """Get certificate version."""
        return cert.version.value

    @staticmethod
    def get_signature_algorithm(cert: x509.Certificate) -> str:
        """Get signature algorithm name."""
        return cert.signature_algorithm_oid._name

    @staticmethod
    def is_self_signed(cert: x509.Certificate) -> bool:
        """Check if certificate is self-signed."""
        return cert.subject == cert.issuer

    @staticmethod
    def is_ca(cert: x509.Certificate) -> bool:
        """Check if certificate is a CA certificate."""
        try:
            basic_constraints = cert.extensions.get_extension_for_oid(
                ExtensionOID.BASIC_CONSTRAINTS
            )
            return basic_constraints.value.ca
        except x509.ExtensionNotFound:
            return False

    @staticmethod
    def get_key_usage(cert: x509.Certificate) -> List[str]:
        """Get key usage extensions."""
        try:
            key_usage = cert.extensions.get_extension_for_oid(ExtensionOID.KEY_USAGE)
            usages = []
            if key_usage.value.digital_signature:
                usages.append("digital_signature")
            if key_usage.value.key_encipherment:
                usages.append("key_encipherment")
            if key_usage.value.key_cert_sign:
                usages.append("key_cert_sign")
            if key_usage.value.crl_sign:
                usages.append("crl_sign")
            return usages
        except x509.ExtensionNotFound:
            return []

    @staticmethod
    def get_extended_key_usage(cert: x509.Certificate) -> List[str]:
        """Get extended key usage extensions."""
        try:
            ext_key_usage = cert.extensions.get_extension_for_oid(
                ExtensionOID.EXTENDED_KEY_USAGE
            )
            return [oid._name for oid in ext_key_usage.value]
        except x509.ExtensionNotFound:
            return []

    @staticmethod
    def to_pem(cert: x509.Certificate) -> str:
        """Convert certificate to PEM format."""
        return cert.public_bytes(serialization.Encoding.PEM).decode("utf-8")

    @staticmethod
    def to_der(cert: x509.Certificate) -> bytes:
        """Convert certificate to DER format."""
        return cert.public_bytes(serialization.Encoding.DER)

    @staticmethod
    def get_all_info(cert: x509.Certificate) -> Dict:
        """Get all certificate information as dictionary."""
        not_before, not_after = CertificateParser.get_validity_period(cert)

        return {
            "version": CertificateParser.get_version(cert),
            "serial_number": CertificateParser.get_serial_number(cert),
            "subject": CertificateParser.get_subject(cert),
            "subject_cn": CertificateParser.get_subject_cn(cert),
            "issuer": CertificateParser.get_issuer(cert),
            "issuer_cn": CertificateParser.get_issuer_cn(cert),
            "not_before": not_before.isoformat(),
            "not_after": not_after.isoformat(),
            "san": CertificateParser.get_san(cert),
            "fingerprint_sha256": CertificateParser.get_fingerprint(cert, "sha256"),
            "fingerprint_sha1": CertificateParser.get_fingerprint(cert, "sha1"),
            "public_key": CertificateParser.get_public_key_info(cert),
            "signature_algorithm": CertificateParser.get_signature_algorithm(cert),
            "is_self_signed": CertificateParser.is_self_signed(cert),
            "is_ca": CertificateParser.is_ca(cert),
            "key_usage": CertificateParser.get_key_usage(cert),
            "extended_key_usage": CertificateParser.get_extended_key_usage(cert),
        }
