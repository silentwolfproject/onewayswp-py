<div align="center">

<img src="https://raw.githubusercontent.com/silentwolfproject/onewayswp-py/main/assets/banner.png" alt="OnewaySWP Banner" width="100%">

<br>

# ONEWAYSWP

### Offline One-Way License Framework

**Secure · Offline · Portable · Self-Contained**

</div>

---

<div align="center">

[![Version](https://img.shields.io/badge/version-0.1.0-blue?style=for-the-badge)](#project-information)
[![Python](https://img.shields.io/badge/Python-Compatible-yellow?style=for-the-badge\&logo=python\&logoColor=white)](#installation)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](#project-information)
[![Platform](https://img.shields.io/badge/Platform-Cross--Platform-purple?style=for-the-badge)](#compatibility)

</div>

---

> **OnewaySWP** is a Python library for building **one-way license verification systems without requiring a server**.
>
> Licenses are generated on the admin side, distributed to clients, and verified entirely offline.
>
> The framework internally handles **license generation, cryptographic signing, protected local state, and verification**. Client applications only require a **public key** to validate licenses.
>
> **No internet connection. No license server. No backend infrastructure.**

OnewaySWP is designed for developers who want a practical licensing solution that stays portable, self-contained, and independent.

---

## ✦ Features

|     | Feature                       | Description                                                       |
| :-: | ----------------------------- | ----------------------------------------------------------------- |
|  ◉  | **Offline Verification**      | No internet connection or license server required                 |
|  ◉  | **Auto-Detection**            | Automatically detects the current OS and architecture             |
|  ◉  | **Cross-Platform**            | Supports Windows, Linux, macOS, and Android                       |
|  ◉  | **Multi-Mode**                | Supports Date, Credit, and Duration license types                 |
|  ◉  | **Session-Based Duration**    | Duration licenses measured during active sessions                 |
|  ◉  | **Credit System**             | Credit-based licenses with automatic decrement                    |
|  ◉  | **Cryptographic Protection**  | License integrity and tamper detection                            |
|  ◉  | **Protected Local Storage**   | Local license state protected with internal protection mechanisms |
|  ◉  | **Clock Rollback Protection** | Detects system clock manipulation                                 |
|  ◉  | **Multi-License Support**     | Multiple independent license states per application               |
|  ◉  | **Session Context Manager**   | Automatic start/stop for duration licenses                        |
|  ◉  | **State Export & Import**     | Move license state between environments                           |
|  ◉  | **Retry on File Lock**        | Automatic retry when state file is locked                         |

---

# Installation

Install directly from PyPI:

```bash
pip install onewayswp
```

| Command     | Purpose                  |
| ----------- | ------------------------ |
| `pip`       | Python package installer |
| `install`   | Installs a package       |
| `onewayswp` | OnewaySWP package        |

---

# Quick Start

## 01 — Admin Setup

Create an admin instance and generate the key pair.

```python
from onewayswp import Admin

# Create admin instance
admin = Admin()

# Generate secret key and public key
secret, public = admin.generate_keys(auto_save=True)

# Display keys
print("Secret:", secret)
print("Public:", public)
```

> **Important:** The secret key is used to create licenses and must remain private.
> The public key is distributed to client applications for verification.

---

## 02 — Create a License

Load the existing keys and create a license.

```python
from onewayswp import Admin

admin = Admin()

# Load existing keys
admin.load_keys(auto_generate=False)

# Create a license
result = admin.create_license(
    type="date",
    expires="2027-12-31",
    additional_data={
        "client_name": "PT Jaya Abadi"
    }
)

print(result["token"])
```

---

## 03 — Client Verification

The client application only needs the public key.

```python
from onewayswp import Client

# Create client instance
client = Client("data/license.swpb")

# Load public key
client.open_key("~/.owswp/public.key")

# Check whether a license is already active
if not client.is_active():

    token = input("Enter key: ")

    # Validate license
    result = client.validate_key(token)

    if not result["status"]:
        print(result["message"])
        exit(1)

# Verify protection state
protection = client.protection_verify()

if protection["status"]:
    print("Application running...")
else:
    print(protection["message"])
```

### Basic Flow

```text
┌─────────────────────┐
│        ADMIN        │
├─────────────────────┤
│ Generate Key Pair   │
│         ↓           │
│ Create License      │
│         ↓           │
│ Distribute Token    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│       CLIENT        │
├─────────────────────┤
│ Public Key          │
│         ↓           │
│ Validate Token      │
│         ↓           │
│ Verify Local State  │
└─────────────────────┘
```

---

# License Types

OnewaySWP provides three license modes.

## Date License

A license that expires on a specific date.

```python
result = admin.create_license(
    type="date",
    expires="2027-12-31"
)
```

| Parameter | Description                            |
| --------- | -------------------------------------- |
| `type`    | `"date"`                               |
| `expires` | Expiration date in `YYYY-MM-DD` format |

Returns information such as:

* `token`
* `type`
* `expired`
* `expires_at`

---

## Credit License

A license containing a credit balance that decreases when used.

```python
result = admin.create_license(
    type="credit",
    credits=100
)
```

| Parameter | Description           |
| --------- | --------------------- |
| `type`    | `"credit"`            |
| `credits` | Initial credit amount |

Returns information such as:

* `token`
* `type`
* `credit_value`

---

## Duration License

A license valid for a fixed amount of active usage time.

```python
result = admin.create_license(
    type="duration",
    hours=2
)
```

| Parameter          | Description                     |
| ------------------ | ------------------------------- |
| `type`             | `"duration"`                    |
| `hours`            | Duration in hours               |
| `duration_seconds` | Alternative duration in seconds |

Returns information such as:

* `token`
* `type`
* `duration_hours`

---

# API Reference

## Admin

| Method            | Parameters                                                                | Returns | Description              |
| ----------------- | ------------------------------------------------------------------------- | ------- | ------------------------ |
| `__init__`        | `key_dir: str = None`                                                     | `Admin` | Create admin instance    |
| `keys_exist`      | `key_dir: str = None`                                                     | `bool`  | Check if key files exist |
| `generate_keys`   | `auto_save: bool = True, file_path: str = None`                           | `tuple` | Generate key pair        |
| `save_keys`       | `target_dir: str = None`                                                  | `None`  | Save keys to disk        |
| `load_keys`       | `key_dir: str = None, validate: bool = True, auto_generate: bool = False` | `tuple` | Load keys                |
| `set_keys`        | `secret_key: str, public_key: str, validate: bool = True`                 | `None`  | Set keys manually        |
| `validate_keys`   | `none`                                                                    | `bool`  | Verify key pair          |
| `create_license`  | `type, expires, credits, duration_seconds, hours, additional_data`        | `dict`  | Create license token     |
| `regenerate_keys` | `key_dir: str = None`                                                     | `tuple` | Generate new key pair    |
| `platform`        | `none`                                                                    | `dict`  | Get OS and architecture  |
| `version`         | `none`                                                                    | `str`   | Get library version      |

---

## Client

| Method              | Parameters                                             | Returns   | Description                      |
| ------------------- | ------------------------------------------------------ | --------- | -------------------------------- |
| `__init__`          | `data_path: str = None, extra_paths: List[str] = None` | `Client`  | Create client instance           |
| `open_key`          | `path: str`                                            | `None`    | Load public key                  |
| `set_public_key`    | `key: str`                                             | `None`    | Set public key                   |
| `is_active`         | `none`                                                 | `bool`    | Check active license             |
| `validate_key`      | `token: str`                                           | `dict`    | Validate license                 |
| `inspect_key`       | `token: str`                                           | `dict`    | Inspect token without activation |
| `protection_verify` | `none`                                                 | `dict`    | Verify local protection state    |
| `use_credit`        | `amount: int = 1`                                      | `dict`    | Decrement credits                |
| `session`           | `none`                                                 | `context` | Duration session context         |
| `export_state`      | `none`                                                 | `dict`    | Export license state             |
| `import_state`      | `data: dict or str`                                    | `dict`    | Import license state             |
| `status`            | `none`                                                 | `dict`    | Get last status                  |
| `state_path`        | `none`                                                 | `str`     | Get state file path              |
| `reset`             | `none`                                                 | `None`    | Delete local state               |
| `version`           | `none`                                                 | `str`     | Get library version              |

---

## Info Object

The `info` object provides library information and supports both attribute-style and dictionary-style access.

| Method         | Description                |
| -------------- | -------------------------- |
| `__getattr__`  | Access field as attribute  |
| `__getitem__`  | Access field by key        |
| `__contains__` | Check whether field exists |
| `__iter__`     | Iterate over field names   |
| `keys()`       | Get field names            |
| `values()`     | Get field values           |
| `items()`      | Get field/value pairs      |
| `get()`        | Get field with default     |
| `to_dict()`    | Convert to dictionary      |

---

# Response Format

Validation and operation methods use a consistent dictionary-based response format.

## Success

```python
{
    "status": True,
    "code": "SUCCESS",
    "message": "License valid and activated",
    "type": "credit",
    "credit_value": 100,
    "remaining_credits": 100,
    "created_at": "2026-10-03 12:00:00",
    "last_time": "2026-10-03 12:05:00",
    "additional_data": {
        "client_name": "PT Jaya Abadi"
    }
}
```

## Failure

```python
{
    "status": False,
    "code": "EXPIRED",
    "message": "Token expired"
}
```

Failure responses contain:

```text
status
code
message
```

---

# Data Dictionary

## Common Fields

| Field     | Type   | Description                     |
| --------- | ------ | ------------------------------- |
| `status`  | `bool` | True when operation succeeds    |
| `code`    | `str`  | Status or error code            |
| `message` | `str`  | Human-readable message          |
| `type`    | `str`  | `date`, `credit`, or `duration` |

## Date License

| Field            | Type  | Description               |
| ---------------- | ----- | ------------------------- |
| `expired`        | `str` | Expiration date           |
| `expires_at`     | `int` | Unix expiration timestamp |
| `remaining_days` | `int` | Remaining days            |

## Credit License

| Field               | Type  | Description                   |
| ------------------- | ----- | ----------------------------- |
| `credit_value`      | `int` | Initial credit                |
| `remaining_credits` | `int` | Remaining credit              |
| `used`              | `int` | Credit used in last operation |

## Duration License

| Field               | Type    | Description               |
| ------------------- | ------- | ------------------------- |
| `duration_hours`    | `float` | Total duration            |
| `duration_seconds`  | `int`   | Total duration in seconds |
| `remaining_hours`   | `float` | Remaining duration        |
| `remaining_seconds` | `int`   | Remaining seconds         |
| `elapsed_seconds`   | `int`   | Elapsed session time      |
| `started_at`        | `str`   | Session start             |
| `stopped_at`        | `str`   | Session stop              |

## Session

| Field        | Type  | Description                 |
| ------------ | ----- | --------------------------- |
| `created_at` | `str` | License creation timestamp  |
| `last_time`  | `str` | Last verification timestamp |

---

# Error Codes

| Code                      | Description                       |
| ------------------------- | --------------------------------- |
| `SUCCESS`                 | Operation completed successfully  |
| `INVALID_SIGNATURE`       | Token signature is invalid        |
| `INVALID_MAGIC`           | File format is invalid            |
| `INVALID_KEY_FORMAT`      | Key format is invalid             |
| `UNSUPPORTED_VERSION`     | File version is not supported     |
| `KEY_MISMATCH`            | Key pair does not match           |
| `SECURITY_ERROR`          | Security violation detected       |
| `EXPIRED`                 | Token has expired                 |
| `CLOCK_ROLLBACK_DETECTED` | System clock rollback detected    |
| `CORRUPTED_FILE`          | File is corrupted                 |
| `INSUFFICIENT_CREDITS`    | Credit balance is insufficient    |
| `FILE_LOCKED`             | File is locked by another process |
| `IO_ERROR`                | Input/output error                |
| `CRYPTO_ERROR`            | Cryptographic error               |
| `SERIALIZATION_ERROR`     | Serialization error               |
| `FFI_ERROR`               | Foreign function interface error  |
| `NO_STATE_FILE`           | State file does not exist         |

---

# Examples

## Generate Keys

```python
from onewayswp import Admin

admin = Admin(key_dir="./keys")

secret, public = admin.generate_keys(
    auto_save=True
)

print("Secret Key:", secret)
print("Public Key:", public)
```

---

## Load Existing Keys

```python
from onewayswp import Admin

admin = Admin()

secret, public = admin.load_keys(
    validate=True,
    auto_generate=False
)

print("Keys loaded successfully")
```

---

## Load Keys with Auto-Generate

```python
from onewayswp import Admin

admin = Admin()

secret, public = admin.load_keys(
    auto_generate=True
)

print("Keys ready")
print("Public:", public)
```

---

## Create Date License

```python
from onewayswp import Admin

admin = Admin()
admin.load_keys()

result = admin.create_license(
    type="date",
    expires="2027-12-31",
    additional_data={
        "client_name": "PT Jaya Abadi",
        "plan": "pro"
    }
)

token = result["token"]

print("Token:", token)
print("Expires:", result["expired"])
print("Expires at:", result["expires_at"])
```

---

## Create Credit License

```python
from onewayswp import Admin

admin = Admin()
admin.load_keys()

result = admin.create_license(
    type="credit",
    credits=100,
    additional_data={
        "client_name": "Toko ABC"
    }
)

print("Token:", result["token"])
print("Credits:", result["credit_value"])
```

---

## Create Duration License

```python
from onewayswp import Admin

admin = Admin()
admin.load_keys()

result = admin.create_license(
    type="duration",
    hours=2,
    additional_data={
        "client_name": "User XYZ"
    }
)

print("Token:", result["token"])
print("Duration:", result["duration_hours"], "hours")
```

Alternative using seconds:

```python
result = admin.create_license(
    type="duration",
    duration_seconds=3600
)

print(
    "Duration:",
    result["duration_hours"],
    "hours"
)
```

---

## Set Keys Manually

```python
from onewayswp import Admin

admin = Admin()

admin.set_keys(
    secret_key="OWSWP-sec-...",
    public_key="OWSWP-pub-...",
    validate=True
)

print("Keys set")
```

---

## Regenerate Keys

```python
from onewayswp import Admin

admin = Admin()
admin.load_keys()

new_secret, new_public = admin.regenerate_keys()

print("New secret:", new_secret)
print("New public:", new_public)
```

> Regenerating the key pair will cause previously issued tokens to become invalid.

---

## Platform Information

```python
from onewayswp import Admin

admin = Admin()

info = admin.platform()

print("OS:", info["os"])
print("Arch:", info["arch"])
```

---

## Client Validation

```python
from onewayswp import Client

client = Client(
    "data/license.swpb"
)

client.set_public_key(
    "OWSWP-pub-..."
)

if client.is_active():

    print("License already active")

else:

    token = input("Enter key: ")

    result = client.validate_key(token)

    if result["status"]:

        print("License activated")
        print("Type:", result["type"])

    else:

        print("Failed:", result["message"])
```

---

## Use Credits

```python
from onewayswp import Client

client = Client(
    "data/license.swpb"
)

client.open_key(
    "~/.owswp/public.key"
)

result = client.validate_key(
    "OWSWP-..."
)

if not result["status"]:
    print("Invalid license")
    exit(1)

result = client.use_credit(5)

if result["status"]:

    print("Used 5 credits")
    print(
        "Remaining:",
        result["remaining_credits"]
    )

else:

    print("Failed:", result["message"])
```

---

## Duration Session

Duration licenses can measure usage during an active session.

```python
from onewayswp import Client
import time

client = Client(
    "data/license.swpb"
)

client.open_key(
    "~/.owswp/public.key"
)

result = client.validate_key(
    "OWSWP-..."
)

if not result["status"]:
    print("Invalid license")
    exit(1)

with client.session():

    print("Application running...")

    time.sleep(10)

protection = client.protection_verify()

print(
    "Remaining:",
    protection["remaining_hours"],
    "hours"
)
```

---

## Inspect License Without Activating

```python
from onewayswp import Client

client = Client(
    "data/license.swpb"
)

client.set_public_key(
    "OWSWP-pub-..."
)

result = client.inspect_key(
    "OWSWP-..."
)

if result["status"]:

    print("Type:", result["type"])
    print("Is expired:", result["is_expired"])

    if result["type"] == "date":

        print(
            "Expires:",
            result["expired"]
        )

        print(
            "Remaining days:",
            result["remaining_days"]
        )

    elif result["type"] == "credit":

        print(
            "Credits:",
            result["credit_value"]
        )

    elif result["type"] == "duration":

        print(
            "Duration hours:",
            result["duration_hours"]
        )
```

---

## Export & Import State

Export state:

```python
from onewayswp import Client

client1 = Client(
    "data/license1.swpb"
)

client1.open_key(
    "~/.owswp/public.key"
)

exported = client1.export_state()

print(
    "Exported data:",
    exported["data"][:50],
    "..."
)

print(
    "Public key:",
    exported["public_key"]
)
```

Import state:

```python
client2 = Client(
    "data/license2.swpb"
)

client2.set_public_key(
    exported["public_key"]
)

result = client2.import_state(
    exported
)

if result["status"]:

    print(
        "State imported successfully"
    )
```

---

## Reset Client State

```python
from onewayswp import Client

client = Client(
    "data/license.swpb"
)

client.set_public_key(
    "OWSWP-pub-..."
)

client.reset()

print("State reset")
```

After resetting, the next validation will require a new token.

---

# Library Information

```python
from onewayswp import info

print(info)

print("Author:", info.author)
print("Version:", info.oneway_version)
print("GitHub:", info.swp_github)
```

Dictionary-style access:

```python
print("Author:", info["author"])
```

Convert to dictionary:

```python
data = info.to_dict()

for key, value in data.items():
    print(f"{key}: {value}")
```

---

# Error Handling

```python
from onewayswp import (
    Client,
    OnewaySWPError,
    InvalidTokenError,
    ExpiredError,
    SecurityError,
)

client = Client(
    "data/license.swbp"
)

client.set_public_key(
    "OWSWP-pub-..."
)

try:

    result = client.validate_key(
        "OWSWP-..."
    )

    if not result["status"]:

        code = result["code"]
        message = result["message"]

        print(
            f"Error [{code}]: {message}"
        )

except InvalidTokenError as e:

    print(
        f"Invalid token: {e}"
    )

except ExpiredError as e:

    print(
        f"Token expired: {e}"
    )

except SecurityError as e:

    print(
        f"Security error: {e}"
    )

except OnewaySWPError as e:

    print(
        f"Error: {e}"
    )
```

---

# Security Notes

OnewaySWP is designed to help developers create **one-way license verification systems for applications that cannot rely on a server**.

It is a licensing framework, **not a replacement for application-level security**.

The library applies internal cryptographic protection to help preserve license integrity, protect local license state, and detect unauthorized modification.

However, the overall security of an application still depends on how the framework is integrated by the developer.

Any bypass, modification, or direct interaction with the application code is outside the scope of this library.

### Keep Your Secret Key Private

The secret key is used to sign licenses.

**Never distribute it with client applications.**

If the secret key is exposed, another party may be able to generate valid licenses.

### Protect Your Key Pair

Store the secret key and public key safely.

Losing the key pair may prevent future licenses from being verified against previously issued tokens.

### Public Key Distribution

Client applications only require the public key to validate licenses.

The secret key should remain on the administrative side.

### Protect Local State

Treat the `.swpb` state file as protected application data.

Manual modification may invalidate the license state.

### Integration Matters

OnewaySWP is a tool.

The way it is integrated into an application determines how effectively it contributes to the application's licensing protection.

---

# Compatibility

OnewaySWP is designed for cross-platform usage:

```text
Windows
Linux
macOS
Android
```

Platform and architecture information can be detected automatically:

```python
from onewayswp import Admin

admin = Admin()

info = admin.platform()

print(info["os"])
print(info["arch"])
```

---

# Project Information

|                  |                                   |
| ---------------- | --------------------------------- |
| **Project**      | OnewaySWP                         |
| **Description**  | Offline One-Way License Framework |
| **Version**      | `0.1.0`                           |
| **Author**       | Juan Hulu                         |
| **Organization** | SilentWolfProject                 |
| **License**      | MIT                               |

---

# Links

* **Author — TikTok**
  https://tiktok.com/@juanhulu.xyz

* **Project — TikTok**
  https://tiktok.com/@juanhulu.xyz

* **Author — Instagram**
  https://www.instagram.com/juanhulu.xyz

* **Project — Instagram**
  https://www.instagram.com/silentwolfproject

* **GitHub Pages**
  https://silentwolfproject.github.io

---

<div align="center">

## ONEWAYSWP

**Offline licensing without the server.**

Built by **SilentWolfProject**

`v0.1.0` · `MIT License`

</div>
