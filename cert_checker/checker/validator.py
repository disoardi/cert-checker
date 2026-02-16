"""Certificate chain validation."""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

from cryptography import x509
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric import padding, rsa, ec, dsa
from cryptography.x509.oid import ExtensionOID


class ValidationStatus(Enum):
    """Validation status enumeration."""

    VALID = "valid"
    INVALID = "invalid"
    WARNING = "warning"


@dataclass
class ValidationResult:
    """Certificate validation result."""

    status: ValidationStatus
    messages: List[str]
    is_valid: bool


class CertificateValidator:
    """Certificate chain validator."""

    def __init__(self, truststore: Optional[List[x509.Certificate]] = None):
        """
        Initialize validator.

        Args:
            truststore: List of trusted root certificates
        """
        self.truststore = truststore or []

    def add_trusted_cert(self, cert: x509.Certificate) -> None:
        """Add a trusted certificate to truststore."""
        self.truststore.append(cert)

    def verify_signature(
        self, cert: x509.Certificate, issuer_cert: x509.Certificate
    ) -> bool:
        """
        Verify certificate signature against issuer.

        Args:
            cert: Certificate to verify
            issuer_cert: Issuer certificate

        Returns:
            True if signature is valid
        """
        try:
            public_key = issuer_cert.public_key()

            # Get signature algorithm
            sig_algorithm = cert.signature_algorithm_oid._name

            # Verify based on key type
            if isinstance(public_key, rsa.RSAPublicKey):
                # RSA signature verification
                public_key.verify(
                    cert.signature,
                    cert.tbs_certificate_bytes,
                    padding.PKCS1v15(),
                    cert.signature_hash_algorithm,
                )
            elif isinstance(public_key, ec.EllipticCurvePublicKey):
                # ECDSA signature verification
                public_key.verify(
                    cert.signature,
                    cert.tbs_certificate_bytes,
                    ec.ECDSA(cert.signature_hash_algorithm),
                )
            elif isinstance(public_key, dsa.DSAPublicKey):
                # DSA signature verification
                public_key.verify(
                    cert.signature,
                    cert.tbs_certificate_bytes,
                    cert.signature_hash_algorithm,
                )
            else:
                return False

            return True

        except InvalidSignature:
            return False
        except Exception:
            return False

    def check_key_usage(self, cert: x509.Certificate) -> ValidationResult:
        """
        Check key usage extensions.

        Args:
            cert: Certificate to check

        Returns:
            Validation result
        """
        messages = []

        try:
            # Check Key Usage
            key_usage = cert.extensions.get_extension_for_oid(ExtensionOID.KEY_USAGE)

            # For CA certificates
            try:
                basic_constraints = cert.extensions.get_extension_for_oid(
                    ExtensionOID.BASIC_CONSTRAINTS
                )
                if basic_constraints.value.ca:
                    # CA cert should have key_cert_sign
                    if not key_usage.value.key_cert_sign:
                        messages.append("CA certificate missing key_cert_sign usage")
                        return ValidationResult(
                            status=ValidationStatus.INVALID,
                            messages=messages,
                            is_valid=False,
                        )
            except x509.ExtensionNotFound:
                pass

        except x509.ExtensionNotFound:
            messages.append("Key usage extension not found")
            return ValidationResult(
                status=ValidationStatus.WARNING, messages=messages, is_valid=True
            )

        return ValidationResult(
            status=ValidationStatus.VALID, messages=["Key usage valid"], is_valid=True
        )

    def check_basic_constraints(self, cert: x509.Certificate) -> ValidationResult:
        """
        Check basic constraints extension.

        Args:
            cert: Certificate to check

        Returns:
            Validation result
        """
        messages = []

        try:
            basic_constraints = cert.extensions.get_extension_for_oid(
                ExtensionOID.BASIC_CONSTRAINTS
            )

            if basic_constraints.value.ca:
                messages.append("Certificate is a CA certificate")
                if basic_constraints.value.path_length is not None:
                    messages.append(
                        f"Path length constraint: {basic_constraints.value.path_length}"
                    )
            else:
                messages.append("Certificate is not a CA certificate")

        except x509.ExtensionNotFound:
            messages.append("Basic constraints extension not found")
            return ValidationResult(
                status=ValidationStatus.WARNING, messages=messages, is_valid=True
            )

        return ValidationResult(
            status=ValidationStatus.VALID, messages=messages, is_valid=True
        )

    def validate_chain(
        self, cert_chain: List[x509.Certificate], use_truststore: bool = True
    ) -> ValidationResult:
        """
        Validate certificate chain.

        Args:
            cert_chain: Certificate chain (leaf first)
            use_truststore: Whether to validate against truststore

        Returns:
            Validation result
        """
        messages = []

        if not cert_chain:
            return ValidationResult(
                status=ValidationStatus.INVALID,
                messages=["Empty certificate chain"],
                is_valid=False,
            )

        # Validate each certificate in chain
        for i, cert in enumerate(cert_chain):
            # Check basic constraints
            bc_result = self.check_basic_constraints(cert)
            messages.extend([f"Cert {i}: {msg}" for msg in bc_result.messages])

            # Check key usage
            ku_result = self.check_key_usage(cert)
            messages.extend([f"Cert {i}: {msg}" for msg in ku_result.messages])

            if not ku_result.is_valid:
                return ValidationResult(
                    status=ValidationStatus.INVALID,
                    messages=messages,
                    is_valid=False,
                )

        # Verify chain signatures
        for i in range(len(cert_chain) - 1):
            cert = cert_chain[i]
            issuer = cert_chain[i + 1]

            # Verify issuer relationship
            if cert.issuer != issuer.subject:
                messages.append(
                    f"Cert {i}: Issuer does not match next cert in chain"
                )
                return ValidationResult(
                    status=ValidationStatus.INVALID,
                    messages=messages,
                    is_valid=False,
                )

            # Verify signature
            if not self.verify_signature(cert, issuer):
                messages.append(f"Cert {i}: Invalid signature from issuer")
                return ValidationResult(
                    status=ValidationStatus.INVALID,
                    messages=messages,
                    is_valid=False,
                )
            else:
                messages.append(f"Cert {i}: Signature valid")

        # Check root certificate against truststore
        if use_truststore and self.truststore:
            root_cert = cert_chain[-1]
            found_in_truststore = False

            for trusted_cert in self.truststore:
                if root_cert.subject == trusted_cert.subject:
                    # Verify root cert signature with trusted cert
                    if self.verify_signature(root_cert, trusted_cert):
                        found_in_truststore = True
                        messages.append("Root certificate found in truststore")
                        break

            if not found_in_truststore:
                messages.append("Root certificate not found in truststore")
                return ValidationResult(
                    status=ValidationStatus.INVALID,
                    messages=messages,
                    is_valid=False,
                )

        return ValidationResult(
            status=ValidationStatus.VALID,
            messages=messages,
            is_valid=True,
        )

    def validate_single(self, cert: x509.Certificate) -> ValidationResult:
        """
        Validate a single certificate (without chain validation).

        Args:
            cert: Certificate to validate

        Returns:
            Validation result
        """
        messages = []

        # Check basic constraints
        bc_result = self.check_basic_constraints(cert)
        messages.extend(bc_result.messages)

        # Check key usage
        ku_result = self.check_key_usage(cert)
        messages.extend(ku_result.messages)

        if not ku_result.is_valid:
            return ValidationResult(
                status=ValidationStatus.INVALID,
                messages=messages,
                is_valid=False,
            )

        # Check if self-signed
        if cert.subject == cert.issuer:
            if self.verify_signature(cert, cert):
                messages.append("Self-signed certificate with valid signature")
            else:
                messages.append("Self-signed certificate with INVALID signature")
                return ValidationResult(
                    status=ValidationStatus.INVALID,
                    messages=messages,
                    is_valid=False,
                )

        return ValidationResult(
            status=ValidationStatus.VALID,
            messages=messages,
            is_valid=True,
        )
