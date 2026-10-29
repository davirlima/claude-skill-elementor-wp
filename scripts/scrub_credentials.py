#!/usr/bin/env python3
"""Find and redact WordPress application passwords / Basic-auth headers left in Claude Code's local files.

Offboarding step for the end of a project: after `claude mcp remove <name>` the secret is still sitting in
~/.claude.json backups, the prompt history, shell history and the session transcripts (anything the user pasted or
any command that carried the credential). This script discovers the secrets by pattern, then replaces them with
[REMOVIDO]. Secrets are never printed.

Discovery (no secret needs to be typed):
  - `Basic <base64>` headers whose payload is `user:application-password` (also gives the password in all spellings)
  - `Application password: xxxx xxxx xxxx xxxx xxxx xxxx` / `WP_APP_PASSWORD=...` / "app password ..." phrases
  - extra secrets listed one per line in --secret-file

Usage:
  scrub_credentials.py                      # dry run: which files hold secrets (default paths)
  scrub_credentials.py --apply              # redact them (skips files modified in the last --skip-recent minutes)
  scrub_credentials.py --apply --skip-recent 0   # also the live session transcript — only after closing Claude Code
  scrub_credentials.py --paths DIR_OR_FILE ...   # scan elsewhere (scratch dirs, project folders)

Remember: redaction is local housekeeping. The credential itself stays valid until it is revoked in
WordPress -> Users -> Profile -> Application Passwords.
"""
import argparse, base64, binascii, os, re, sys, time

DEFAULT_PATHS = ['~/.claude.json', '~/.claude', '~/.bash_history', '~/.zsh_history']
TEXT_EXT = {'', '.json', '.jsonl', '.md', '.txt', '.log', '.sh', '.py', '.js', '.mjs', '.yaml', '.yml'}
PW = rb'(?:[A-Za-z0-9]{4} ){5}[A-Za-z0-9]{4}'
RE_BASIC = re.compile(rb'Basic ([A-Za-z0-9+/]{16,}={0,2})')
RE_PW = [re.compile(rb'(?i)app(?:lication)?[ _-]?password[^A-Za-z0-9\n]{0,6}\\?"?\s*(' + PW + rb')'),
         re.compile(rb'WP_APP_PASSWORD=\\?"?(' + PW + rb')')]
RE_USER = re.compile(rb'(?i)username[^A-Za-z0-9\n]{0,6}([A-Za-z0-9_.@-]{3,40})')
MASK = b'[REMOVIDO]'


def is_placeholder(pw: bytes) -> bool:
    """'xxxx xxxx …', 'aaaa bbbb …' and similar documentation examples are not secrets."""
    flat = pw.replace(b' ', b'').lower()
    return len(set(flat)) <= 4


def spellings(pw: bytes):
    if is_placeholder(pw): return set()
    p = pw.strip(); flat = p.replace(b' ', b'')
    spaced = b' '.join(flat[i:i + 4] for i in range(0, len(flat), 4)) if len(flat) == 24 else p
    return {p, flat, spaced}


def discover(data: bytes, secrets: set):
    users = set(RE_USER.findall(data))
    for m in RE_BASIC.finditer(data):
        tok = m.group(1)
        try: raw = base64.b64decode(tok + b'=' * (-len(tok) % 4), validate=True)
        except (binascii.Error, ValueError): continue
        if re.fullmatch(rb'[A-Za-z0-9_.@-]{2,60}:[A-Za-z0-9 ]{20,32}', raw):
            user, pw = raw.split(b':', 1)
            if is_placeholder(pw): continue
            users.add(user); secrets.add(tok); secrets |= spellings(pw)
    for rx in RE_PW:
        for m in rx.finditer(data):
            pw = m.group(1); secrets |= spellings(pw)
            for u in users | {b'admin'}:
                for variant in spellings(pw):
                    secrets.add(base64.b64encode(u + b':' + variant))


def files(paths):
    for p in paths:
        p = os.path.expanduser(p)
        if os.path.isfile(p): yield p
        elif os.path.isdir(p):
            for d, _, fs in os.walk(p):
                for f in fs:
                    fp = os.path.join(d, f)
                    if os.path.splitext(f)[1].lower() in TEXT_EXT and os.path.getsize(fp) < 400 * 1024 * 1024: yield fp


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--apply', action='store_true'); ap.add_argument('--paths', nargs='*', default=DEFAULT_PATHS)
    ap.add_argument('--secret-file'); ap.add_argument('--skip-recent', type=int, default=15, help='minutes (default 15)')
    a = ap.parse_args()
    secrets = set()
    if a.secret_file: secrets |= {l.strip().encode() for l in open(a.secret_file) if l.strip()}
    targets = list(files(a.paths))
    for f in targets:
        try: discover(open(f, 'rb').read(), secrets)
        except OSError: pass
    secrets = {s for s in secrets if len(s) >= 20}
    if not secrets: print('no credentials found'); return
    print(f'{len(secrets)} secret spelling(s) discovered (not shown); scanning {len(targets)} files')
    ordered = sorted(secrets, key=len, reverse=True)
    hits = skipped = changed = 0
    for f in targets:
        try: data = open(f, 'rb').read()
        except OSError: continue
        n = sum(data.count(s) for s in ordered)
        if not n: continue
        hits += 1; age = (time.time() - os.path.getmtime(f)) / 60
        if age < a.skip_recent:
            skipped += 1; print(f'  SKIPPED (active, modified {age:.0f} min ago): {f}  [{n} occurrence(s)]'); continue
        print(f'  {"REDACTED" if a.apply else "would redact"}: {f}  [{n} occurrence(s)]')
        if a.apply:
            for s in ordered: data = data.replace(s, MASK)
            st = os.stat(f); tmp = f + '.scrub.tmp'
            with open(tmp, 'wb') as out: out.write(data)
            os.chmod(tmp, st.st_mode); os.utime(tmp, (st.st_atime, st.st_mtime)); os.replace(tmp, f); changed += 1
    print(f'files with secrets: {hits} | redacted: {changed} | skipped (recently modified): {skipped}')
    if skipped: print('Re-run with --skip-recent 0 after closing Claude Code to clean the live session transcript.')
    if not a.apply: print('dry run — nothing changed. Add --apply.')


if __name__ == '__main__':
    main()
