#!/usr/bin/env node
/**
 * Validation script for parquet SQL parameterization
 * 
 * Verifies that all parquet queries use parameterized inputs to prevent SQL injection.
 * This script scans the server code for patterns that indicate string interpolation
 * in SQL queries, which would be a security vulnerability.
 */

const fs = require('fs');
const path = require('path');

const RED = '\x1b[31m';
const GREEN = '\x1b[32m';
const YELLOW = '\x1b[33m';
const RESET = '\x1b[0m';

const serverDir = path.join(__dirname, 'app', 'server');
const files = ['teams.ts', 'players.ts', 'games.ts', 'parquet.ts'];

let errors = 0;
let warnings = 0;

console.log('🔍 Validating parquet SQL parameterization...\n');

for (const file of files) {
    const filePath = path.join(serverDir, file);
    if (!fs.existsSync(filePath)) {
        console.log(`${YELLOW}⚠${RESET}  ${file}: File not found (skipping)`);
        warnings++;
        continue;
    }

    const content = fs.readFileSync(filePath, 'utf8');
    const lines = content.split('\n');

    // Check for vulnerable patterns in SQL strings
    const vulnerablePatterns = [
        // String interpolation in SQL WHERE clauses
        { pattern: /WHERE\s+\w+\s*=\s*['"`]\$\{/, desc: 'WHERE clause with template literal interpolation' },
        { pattern: /WHERE\s+\w+\s*=\s*'\s*\+/, desc: 'WHERE clause with string concatenation' },
        
        // String interpolation in read_parquet calls
        { pattern: /read_parquet\s*\(\s*['"`].*\$\{/, desc: 'read_parquet with template literal path' },
    ];

    // Check for safe patterns (evidence of parameterization)
    const safePatterns = [
        { pattern: /parquetQuery.*,\s*\[/, desc: 'parquetQuery called with parameters array' },
        { pattern: /WHERE\s+\w+\s*=\s*\?/, desc: 'WHERE clause using ? placeholder' },
        { pattern: /read_parquet\s*\(\s*\?/, desc: 'read_parquet using ? placeholder' },
    ];

    let fileHasVulnerability = false;
    let fileHasSafePattern = false;

    // Scan for vulnerabilities
    for (const { pattern, desc } of vulnerablePatterns) {
        for (let i = 0; i < lines.length; i++) {
            if (pattern.test(lines[i])) {
                console.log(`${RED}✗${RESET}  ${file}:${i + 1} - ${desc}`);
                console.log(`     ${lines[i].trim()}`);
                fileHasVulnerability = true;
                errors++;
            }
        }
    }

    // Check for safe patterns
    for (const { pattern, desc } of safePatterns) {
        if (pattern.test(content)) {
            fileHasSafePattern = true;
        }
    }

    // Report file status
    if (!fileHasVulnerability && fileHasSafePattern) {
        console.log(`${GREEN}✓${RESET}  ${file}: Parameterized queries detected`);
    } else if (!fileHasVulnerability && !fileHasSafePattern) {
        console.log(`${YELLOW}⚠${RESET}  ${file}: No SQL queries found`);
        warnings++;
    }
}

console.log('\n' + '─'.repeat(50));

if (errors > 0) {
    console.log(`${RED}✗ FAILED${RESET}: Found ${errors} SQL injection vulnerability(ies)`);
    console.log(`\nAll SQL queries must use parameterized inputs (? placeholders).`);
    console.log(`Example:`);
    console.log(`  ❌ WHERE div = '\${div}'`);
    console.log(`  ✅ WHERE div = ?`);
    console.log(`     parquetQuery(sql, label, [div])`);
    process.exit(1);
} else if (warnings > 0) {
    console.log(`${YELLOW}⚠${RESET}  Passed with ${warnings} warning(s)`);
    process.exit(0);
} else {
    console.log(`${GREEN}✓ PASSED${RESET}: All parquet queries use parameterized inputs`);
    process.exit(0);
}
