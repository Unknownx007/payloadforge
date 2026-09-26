# Changelog

## [0.1.0] — 2025-09-26

### Added
- Interactive DEDSEC shell with tab completion and persistent history
- 14 Linux reverse shell payloads (bash, python, python+PTY, perl, ruby, php, node, socat, awk, nc, ncat)
- 6 Windows payloads (PowerShell, cmd-wrapped PowerShell, encoded PowerShell, IEX, mshta, certutil)
- 11 cloud payloads (AWS IMDS v1+v2, S3, SSM, Kubernetes SA theft, pod creation, secrets)
- 9 web payloads (JSP, PHP, ASPX — reverse shells and webshells)
- 6 tunnel payloads (SSH reverse, dynamic SOCKS, port-forward, chisel, socat)
- 6 chain/dropper payloads
- 7 encoders (base64, base64_nl, utf16le_b64, hex, url, gzip_b64, rev)
- 9 obfuscators (vars, split_strings, ps_case_flip, ps_backticks, ps_concat_chain, double_b64)
- TCP listener with raw interactive shell pipe
- TLS listener with auto-generated self-signed certificate
- HTTP payload server for stagers and download-and-execute
- `verify`, `testall`, `checkdeps` local verification commands
- GitHub Actions Windows test workflow

### Verified
- **Arch Linux, Python 3.14:** 14/14 Linux payloads, 7/7 encoders, 9/9 obfuscators, TLS handshake, 4/4 chain droppers, PHP webshell
- **Windows Server 2022 (GitHub Actions):** `powershell_tcp`, `cmd_powershell`

### Known limitations
- Cloud, tunnel, and web (JSP/ASPX) payloads are correct templates but require real infrastructure to test
- `mshta`, `certutil_download`, and `powershell_iex_web` require real Windows — not in CI matrix yet

[0.1.0]: https://github.com/Unknownx007/payloadforge/releases/tag/v0.1.0
