import fs from 'fs';
import path from 'path';

/**
 * Recursively loads all JSON files from a structured test folder.
 * @param {string} rootDir - Path to the root test folder.
 * @returns {object} Nested dictionary of JSON contents.
 */
export function loadTestCases(rootDir) {
  const cases = {};

  const groups = fs.readdirSync(rootDir, { withFileTypes: true })
    .filter(dirent => dirent.isDirectory());

  for (const group of groups) {
    const groupPath = path.join(rootDir, group.name);
    cases[group.name] = {};

    const stages = fs.readdirSync(groupPath, { withFileTypes: true })
      .filter(dirent => dirent.isDirectory());

    for (const stage of stages) {
      const stagePath = path.join(groupPath, stage.name);
      cases[group.name][stage.name] = {};

      const files = fs.readdirSync(stagePath)
        .filter(file => file.endsWith('.json'));

      for (const file of files) {
        const testId = path.basename(file, '.json');
        const filePath = path.join(stagePath, file);
        const content = JSON.parse(fs.readFileSync(filePath, 'utf-8'));
        cases[group.name][stage.name][testId] = content;
      }
    }
  }

  return cases;
}