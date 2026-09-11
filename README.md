# Novara Data Centre Programme — public site

Public-safe deployment repository for the Novara Data Centre Programme site.
It contains only the reviewed site source and build controls exported from the
private owner-side programme repository.

This repository must not contain programme models, investor terms, diligence
documents, correspondence, personal information, or credentials.

```bash
./scripts/build-site.sh
python3 scripts/verify-site.py
```

The deployed site is intentionally marked `noindex, nofollow`. That reduces
discovery but does not make the site private.
