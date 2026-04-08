# Dev Profile Transfer

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg?style=flat-square&logo=python)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](https://opensource.org/licenses/MIT)
[![GitHub Stars](https://img.shields.io/github/stars/placeholder/dev-profile-transfer?style=flat-square&logo=github)](https://github.com/placeholder/dev-profile-transfer)

**Dev Profile Transfer** is a secure, offline-first CLI tool designed to capture, export, and share developer environment profiles. It allows Software Engineers, DevOps Engineers, and Tech Leads to maintain consistent shell configurations across multi-machine development environments. By capturing environment variables, aliases, and shell settings, it ensures portability and reduces onboarding friction while safeguarding sensitive credentials.

## Features

*   **Environment Capture**: Instantly snapshots current shell state including variables, aliases, and shell configuration settings.
*   **Secure Exporting**: Sanitizes sensitive data (secrets, keys) before creating portable JSON or YAML profile files.
*   **Multi-Format Support**: Exports profiles in both JSON and YAML formats with version metadata for backward compatibility.
*   **Encryption Support**: Optional AES-based encryption for team-shared profiles using the `cryptography` library.
*   **Environment Validation**: Pre-apply checks to verify exported profiles match target environment constraints.
*   **Profile Diffing**: Highlights environmental drift between two different profile configurations to catch inconsistencies.
*   **One-Click Restoration**: Applies exported configurations seamlessly back into the current user shell environment.

## Installation

Install the tool via Py