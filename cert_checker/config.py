"""Configuration parser for cert-checker."""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional

import toml
from pydantic import BaseModel, Field, field_validator


class StoreConfig(BaseModel):
    """Store configuration."""

    truststore: Optional[str] = None
    truststore_password: Optional[str] = None
    keystore: Optional[str] = None
    keystore_password: Optional[str] = None

    @field_validator("truststore_password", "keystore_password", mode="before")
    @classmethod
    def expand_env_vars(cls, v: Optional[str]) -> Optional[str]:
        """Expand environment variables in password fields."""
        if v is None:
            return None
        # Support ${VAR_NAME} syntax
        pattern = re.compile(r"\$\{([^}]+)\}")
        matches = pattern.findall(v)
        for match in matches:
            env_value = os.environ.get(match, "")
            v = v.replace(f"${{{match}}}", env_value)
        return v


class HostConfig(BaseModel):
    """Host configuration."""

    name: str
    fqdn: str
    port: int = Field(default=443, ge=1, le=65535)
    enabled: bool = True
    warning_days: int = Field(default=30, ge=0)
    client_cert: bool = False

    @field_validator("fqdn")
    @classmethod
    def validate_fqdn(cls, v: str) -> str:
        """Validate FQDN format."""
        if not v or len(v) > 253:
            raise ValueError("Invalid FQDN length")
        # Basic FQDN validation
        parts = v.split(".")
        if len(parts) < 2:
            raise ValueError("FQDN must have at least two parts")
        for part in parts:
            if not part or len(part) > 63:
                raise ValueError("Invalid FQDN part length")
            if not re.match(r"^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?$", part):
                raise ValueError("Invalid FQDN format")
        return v


class SettingsConfig(BaseModel):
    """General settings."""

    timeout: int = Field(default=10, ge=1, le=300)
    verify_chain: bool = True
    show_warnings: bool = True
    default_port: int = Field(default=443, ge=1, le=65535)


class Config(BaseModel):
    """Main configuration."""

    settings: SettingsConfig = Field(default_factory=SettingsConfig)
    stores: StoreConfig = Field(default_factory=StoreConfig)
    hosts: List[HostConfig] = Field(default_factory=list)

    @classmethod
    def from_file(cls, path: Path) -> "Config":
        """Load configuration from TOML file."""
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")

        with open(path, "r") as f:
            data = toml.load(f)

        return cls(**data)

    @classmethod
    def from_dict(cls, data: Dict) -> "Config":
        """Create configuration from dictionary."""
        return cls(**data)

    def get_enabled_hosts(self) -> List[HostConfig]:
        """Get list of enabled hosts."""
        return [host for host in self.hosts if host.enabled]

    def get_host_by_name(self, name: str) -> Optional[HostConfig]:
        """Get host configuration by name."""
        for host in self.hosts:
            if host.name == name:
                return host
        return None
