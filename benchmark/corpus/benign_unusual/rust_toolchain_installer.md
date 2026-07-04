---
name: rust-toolchain-installer
description: >
  Installs the Rust toolchain using rustup, the official Rust installer
  maintained by the Rust Foundation. Sets up the stable channel, common
  targets, and frequently used cargo extensions. Documented with explicit
  notes on what the installer script does and why shell-piped execution
  is the supported method.
capabilities:
  - network
  - execute
version: "1.0"
author: self-authored
license: MIT
---

# Rust Toolchain Installer

Sets up a complete Rust development environment using `rustup`, the official
toolchain manager published by the Rust Foundation at https://rustup.rs.

## Why `curl | sh`?

Rustup's install method is `curl https://sh.rustup.rs | sh`. This is the
official documented installation method from the Rust Foundation and is
documented at https://www.rust-lang.org/tools/install. The script:

1. Detects your OS and architecture.
2. Downloads the appropriate `rustup-init` binary from static.rust-lang.org.
3. Verifies the downloaded binary's SHA256 checksum.
4. Installs `rustup`, `cargo`, and the stable toolchain.

If you want to audit the script first (recommended on shared systems):

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs > /tmp/rustup-init.sh
less /tmp/rustup-init.sh
bash /tmp/rustup-init.sh
```

## Installation

```bash
# Standard one-line install (non-interactive, adds to PATH)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --no-modify-path

# Add Rust to PATH for the current session
source "$HOME/.cargo/env"
```

## Post-Install Setup

```bash
# Verify installation
rustc --version
cargo --version

# Add common targets (e.g. for cross-compilation to musl)
rustup target add x86_64-unknown-linux-musl
rustup target add wasm32-unknown-unknown

# Install frequently used tools
cargo install cargo-watch cargo-audit cargo-expand sccache

# Configure sccache for faster rebuilds
echo 'export RUSTC_WRAPPER=sccache' >> ~/.bashrc
```

## Keeping the Toolchain Updated

```bash
# Update rustup and all installed toolchains
rustup update

# Run security audit on project dependencies
cargo audit
```

## Configuration

| Parameter      | Default  | Description                                               |
|----------------|----------|-----------------------------------------------------------|
| `channel`      | stable   | Toolchain channel: stable, beta, nightly.                 |
| `targets`      | none     | Additional cross-compilation targets to install.          |
| `no_path_mod`  | false    | Skip modifying shell profile files.                       |

## Notes

- The curl-to-sh invocation fetches from `sh.rustup.rs` which is TLS-pinned
  to a certificate owned by the Rust Foundation. This is not a redirect to a
  third-party CDN.
- For CI/CD environments, prefer installing rustup via a package manager
  snapshot or a pre-built Docker image to avoid depending on the network.
- This skill is entirely reproducible; re-running it is idempotent.
