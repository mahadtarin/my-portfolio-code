const { execSync } = require('child_process');
const path = require('path');

function runTests() {
  const testFile = path.resolve(__dirname, './tests/s3conFile.ts');
  const timeout = 600000;
  const reporter = 'mochawesome';

  // Add --extension ts to recognize TypeScript files
  const command = `npx mocha --require ts-node/register --extension ts --reporter ${reporter} --timeout=${timeout} ${testFile}`;
  console.log(`Running command: ${command}`);

  try {
    execSync(command, { stdio: 'inherit' });
  } catch (error) {
    process.exitCode = 1;
  }
}

// Run the function when the script is executed
if (require.main === module) {
  runTests();
}