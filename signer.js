const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

const action = process.argv[2];
const targetFile = process.argv[3];

if (action === 'generate-keys') {
    // Generates your master key pair
    const { publicKey, privateKey } = crypto.generateKeyPairSync('rsa', {
        modulusLength: 4096,
        publicKeyEncoding: { type: 'spki', format: 'pem' },
        privateKeyEncoding: { type: 'pkcs8', format: 'pem' }
    });
    
    fs.writeFileSync('private.pem', privateKey);
    fs.writeFileSync('public.pem', publicKey);
    console.log("Keys forged. Keep 'private.pem' secret and safe! Copy the contents of 'public.pem' into your main.js PUBLIC_KEY variable.");
} 
else if (action === 'sign' && targetFile) {
    // Signs your zip file
    if (!fs.existsSync('private.pem')) return console.error("Error: private.pem not found.");
    
    const privateKey = fs.readFileSync('private.pem', 'utf8');
    const fileData = fs.readFileSync(targetFile);
    
    const signature = crypto.sign(
        'sha256', 
        fileData, 
        { key: privateKey, padding: crypto.constants.RSA_PKCS1_PSS_PADDING }
    );
    
    fs.writeFileSync(targetFile + '.sig', signature);
    console.log(`Successfully forged signature: ${targetFile}.sig`);
} 
else {
    console.log("Commands:\n  node signer.js generate-keys\n  node signer.js sign <file.zip>");
}