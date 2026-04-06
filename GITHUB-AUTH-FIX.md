# GitHub Authentication Blocker (2026-03-17)

## Problem
The `github-app-token.py` script fails with a Python 3.8 compatibility error:

```
TypeError: 'type' object is not subscriptable
  File "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/asymmetric/ec.py", line 522
    _SECT_CURVES: tuple[type[EllipticCurve], ...] = (
```

**Impact:** Cannot push branches or create PRs. Blocks:
- Shipping completed per-game stats feature (4 commits on `feature-per-game-stats` branch)
- All future PR work
- Automated backlog progression

## Root Cause
System is running **Python 3.8.10**, but the installed `cryptography` library uses Python 3.9+ syntax (`tuple[...]` without `from __future__ import annotations`).

## Solutions (Pick One)

### Option 1: Upgrade Python (Recommended)
```bash
sudo apt update
sudo apt install python3.9 python3.9-venv python3-pip
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 1
sudo update-alternatives --config python3  # Select python3.9
pip3 install --upgrade PyJWT cryptography requests
```

### Option 2: Pin Compatible Library Versions
```bash
pip3 install 'cryptography<38.0.0' 'PyJWT>=2.0.0,<3.0.0'
```

### Option 3: Use Existing Node.js Instead
Replace Python token script with Node.js (already at v22.22.0):

```javascript
// ~/.openclaw/github-app-token.js
const jwt = require('jsonwebtoken');
const fs = require('fs');
const https = require('https');

const APP_ID = "2727083";
const INSTALL_ID = "106077172";
const KEY_PATH = "/home/will/sportnumerics-bot-private-key.pem";

const privateKey = fs.readFileSync(KEY_PATH, 'utf8');
const payload = {
    iat: Math.floor(Date.now() / 1000) - 60,
    exp: Math.floor(Date.now() / 1000) + 600,
    iss: APP_ID
};
const jwtToken = jwt.sign(payload, privateKey, { algorithm: 'RS256' });

const options = {
    hostname: 'api.github.com',
    path: `/app/installations/${INSTALL_ID}/access_tokens`,
    method: 'POST',
    headers: {
        'Authorization': `Bearer ${jwtToken}`,
        'Accept': 'application/vnd.github+json',
        'User-Agent': 'sportnumerics-bot'
    }
};

const req = https.request(options, (res) => {
    let data = '';
    res.on('data', chunk => data += chunk);
    res.on('end', () => {
        if (res.statusCode === 201) {
            console.log(JSON.parse(data).token);
        } else {
            console.error(`Error: ${res.statusCode}`, data);
            process.exit(1);
        }
    });
});

req.on('error', e => {
    console.error(e);
    process.exit(1);
});

req.end();
```

Install deps and update TOOLS.md:
```bash
npm install -g jsonwebtoken
# Update TOOLS.md to use: TOKEN=$(node ~/.openclaw/github-app-token.js)
```

## Immediate Workaround (Manual)
Generate token manually and use for one-time push:
```bash
# Generate JWT at https://jwt.io using sportnumerics-bot-private-key.pem
# Exchange for installation token via curl
# Use token to push feature-per-game-stats branch
```

## Validation
After fix, test with:
```bash
cd /home/will/openclaw/sportnumerics-rankings
TOKEN=$(python3 ~/.openclaw/github-app-token.py) && \
  git push https://x-access-token:$TOKEN@github.com/sportnumerics/rankings.git feature-per-game-stats
```

Expected: Branch pushed successfully, ready for PR creation.
