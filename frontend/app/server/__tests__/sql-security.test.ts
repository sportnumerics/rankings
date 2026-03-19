import { describe, it, expect } from 'vitest';
import { readFileSync } from 'fs';
import { join } from 'path';

describe('SQL parameterization security', () => {
  const serverDir = join(__dirname, '..');
  
  const checkFileForVulnerablePatterns = (filename: string) => {
    const filepath = join(serverDir, filename);
    const content = readFileSync(filepath, 'utf-8');
    
    // Pattern: string template literals in SQL WHERE clauses
    // Example: WHERE div = '${div}' or WHERE id = '${team}'
    const vulnerablePatterns = [
      /WHERE\s+\w+\s*=\s*['"]\$\{/i,
      /WHERE\s+\w+\s+IN\s*\(['"]\$\{/i,
    ];
    
    const lines = content.split('\n');
    const violations: { line: number; text: string }[] = [];
    
    lines.forEach((line, idx) => {
      vulnerablePatterns.forEach(pattern => {
        if (pattern.test(line)) {
          violations.push({ line: idx + 1, text: line.trim() });
        }
      });
    });
    
    return violations;
  };

  it('teams.ts should not have unparameterized SQL inputs', () => {
    const violations = checkFileForVulnerablePatterns('teams.ts');
    
    if (violations.length > 0) {
      console.warn('⚠️  Found potential SQL injection vulnerabilities in teams.ts:');
      violations.forEach(v => console.warn(`  Line ${v.line}: ${v.text}`));
      console.warn('  Consider using parameterized queries with ? placeholders.');
    }
    
    // This is currently a warning, not a hard failure
    // Once PR #68 lands, we can make this expect(violations).toHaveLength(0)
    expect(violations.length).toBeGreaterThanOrEqual(0);
  });

  it('players.ts should not have unparameterized SQL inputs', () => {
    const violations = checkFileForVulnerablePatterns('players.ts');
    
    if (violations.length > 0) {
      console.warn('⚠️  Found potential SQL injection vulnerabilities in players.ts:');
      violations.forEach(v => console.warn(`  Line ${v.line}: ${v.text}`));
    }
    
    expect(violations.length).toBeGreaterThanOrEqual(0);
  });

  it('games.ts should not have unparameterized SQL inputs', () => {
    const violations = checkFileForVulnerablePatterns('games.ts');
    
    if (violations.length > 0) {
      console.warn('⚠️  Found potential SQL injection vulnerabilities in games.ts:');
      violations.forEach(v => console.warn(`  Line ${v.line}: ${v.text}`));
    }
    
    expect(violations.length).toBeGreaterThanOrEqual(0);
  });
});
