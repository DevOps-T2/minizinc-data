/**
 * TODO(developer): Uncomment the following lines before running the sample.
 */
// The ID of your GCS bucket
const bucketName = 'minizinc_data';

// The ID of your GCS file
const fileName = 'my_file.mzn';

// Imports the Google Cloud client library
const {Storage} = require('@google-cloud/storage');

// Creates a client
const storage = new Storage({keyFilename: 'key.json'});
const fs = require('fs');

async function generateV4SignedPolicy() {
  const bucket = storage.bucket(bucketName);
  const file = bucket.file(fileName);

  // These options will allow temporary uploading of a file
  // through an HTML form.
  const expires = Date.now() + 60 * 60 * 1000; //  60 minutes
  const options = {
    expires,
    fields: {'x-goog-meta-test': 'data'},
  };

  // Get a v4 signed policy for uploading file
  const [response] = await file.generateSignedPostPolicyV4(options);

  // Create an HTML form with the provided policynode u
  let output = `<form action="${response.url}" method="POST" enctype="multipart/form-data">\n`;
  // Include all fields returned in the HTML form as they're required
  for (const name of Object.keys(response.fields)) {
    const value = response.fields[name];
    output += `  <input name="${name}" value="${value}" type="hidden"/>\n`;
  }
  output += '  <input type="file" name="file"/><br />\n';
  output += '  <input type="submit" value="Upload File"/><br />\n';
  output += '</form>';

  fs.writeFile('./index.html', output, err => {
      if (err) {
          console.log(err)
          return
      }
  })
}

//generateV4SignedPolicy().catch(console.error);

async function generateV4ReadSignedUrl() {
    // These options will allow temporary read access to the file
    const options = {
      version: 'v4',
      action: 'read',
      expires: Date.now() + 60 * 60 * 1000, // 60 minutes
    };                   //min second milli
  
    // Get a v4 signed URL for reading the file
    const [url] = await storage
      .bucket(bucketName)
      .file(fileName)
      .getSignedUrl(options);
  
    console.log('Generated GET signed URL:');
    console.log(url);
    console.log('You can use this URL with any user agent, for example:');
    console.log(`curl '${url}'`);
  }
  

generateV4ReadSignedUrl()