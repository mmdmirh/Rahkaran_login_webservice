/**
 * RSA Password Encryptor for Rahkaran
 * Uses the actual JS libraries from the Rahkaran login page
 * 
 * Usage: node rsa_encrypt.js <password> <rsa_e> <rsa_m> <sessionid>
 * Output: encrypted password in hex format
 * 
 * IMPORTANT: The password is encrypted as: sessionid + "--" + password
 */

const fs = require('fs');
const vm = require('vm');

// Create a sandbox with browser-like globals
const sandbox = {
    console: console,
    Math: Math,
    Array: Array,
    String: String,
    parseInt: parseInt,
    parseFloat: parseFloat,
};

// Load and execute the JS files in order
const bigIntJs = fs.readFileSync(__dirname + '/BigInt.js', 'utf8');
const barrettJs = fs.readFileSync(__dirname + '/Barrett.js', 'utf8');
const rsaJs = fs.readFileSync(__dirname + '/RSA.js', 'utf8');

// Execute in sandbox
vm.createContext(sandbox);
vm.runInContext(bigIntJs, sandbox);
vm.runInContext(barrettJs, sandbox);
vm.runInContext(rsaJs, sandbox);

// Get command line arguments
const args = process.argv.slice(2);

if (args.length < 4) {
    console.error('Usage: node rsa_encrypt.js <password> <rsa_e> <rsa_m> <sessionid>');
    console.error('');
    console.error('The password will be encrypted as: sessionid + "--" + password');
    process.exit(1);
}

const password = args[0];
const rsaE = args[1];
const rsaM = args[2];
const sessionId = args[3];

// The actual string to encrypt: sessionid--password
const stringToEncrypt = sessionId + "--" + password;

// Set max digits for RSA key size (matching Login.js: setMaxDigits(131))
sandbox.setMaxDigits(131);

// Create RSA key and encrypt
const key = new sandbox.RSAKeyPair(rsaE, "", rsaM);
const encrypted = sandbox.encryptedString(key, stringToEncrypt);

// Output the result
console.log(encrypted);
