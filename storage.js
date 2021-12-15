const {Storage} = require('@google-cloud/storage');
const {v4: uuidv4} = require('uuid');

const BUCKET_NAME = 'minizinc_data';

const storage = new Storage({keyFilename: 'key.json'});

async function generatePostSignedPolicy() {
    const bucket = storage.bucket(BUCKET_NAME);
    const fileName = uuidv4();
    const file = bucket.file(fileName);
    
    // link will expire in 15 mins from now.
    const expires = getExpireTime(15);
    const options = {
        expires,
        fields: {'x-goog-meta-test': 'data'}
    };

    var response = await file.generateSignedPostPolicyV4(options);
    response = response[0]
    response.fileUUID = fileName
    console.log(response)
    return response
}

function getExpireTime(minutes) {
    return Date.now() + minutes * 60 * 1000;
}

exports.generatePostSignedPolicy = generatePostSignedPolicy