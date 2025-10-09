import * as payloads from '../api/payloads';
import * as actions from '../api/apiActions';
const assert = require('assert');
const AWS = require('aws-sdk');
require('dotenv').config();

const env= "dev"  // Update this for your environment
const baseURL = `<API_BASE_URL>`;  // Replace with your API base URL
let documentID = "<DOCUMENT_ID_PLACEHOLDER>";  // Replace with your document ID
// Function to list items in the bucket
async function checkXMLFilesInMarkdown() {
    const s3 = new AWS.S3({
        accessKeyId: process.env.AWS_ACCESS_KEY_ID,
        secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
        sessionToken: process.env.AWS_SESSION_TOKEN,
        region: "us-east-1"
    });

    const bucketName = "<AWS_S3_BUCKET_NAME>";  // Replace with your S3 bucket name
    const parentFolder = "<S3_FOLDER_PATH>/";  // Replace with your S3 folder path

    try {
        const params = {
            Bucket: bucketName,
            Prefix: parentFolder, // Only look inside the "markdown files" folder
            Delimiter: "/" // Group by folders
        };

        const data = await s3.listObjectsV2(params).promise();

        if (data.CommonPrefixes && data.CommonPrefixes.length > 0) {
            console.log(`Folders inside "${parentFolder}":`);
            for (const prefix of data.CommonPrefixes) {
                const folderName = prefix.Prefix.split("/").slice(-2, -1)[0]; // Extract folder name
                console.log(`- Checking folder: ${folderName}`);

                // Check if the XML file exists in the folder
                const xmlFileKey = `${prefix.Prefix}${folderName}.xml`;
                const fileParams = {
                    Bucket: bucketName,
                    Key: xmlFileKey
                };

                try {
                    await s3.headObject(fileParams).promise(); // Check if the file exists
                    console.log(`  ✔ Found XML file: ${xmlFileKey}`);
                } catch (error) {
                    if ((error as any).code === "NotFound") {
                        console.log(`  ✘ XML file not found: ${xmlFileKey} \n`);
                    } else {
                        if (error instanceof Error) {
                            console.error(`  Error checking file: ${xmlFileKey}`, error.message);
                        } else {
                            console.error(`  Error checking file: ${xmlFileKey}`, error);
                        }
                    }
                }
            }
        } else {
            console.log(`No folders found inside "${parentFolder}".`);
        }
    } catch (error) {
        if (error instanceof Error) {
            console.error('Error listing folders in "markdown files":', error.message);
        } else {
            console.error('Error listing folders in "markdown files":', error);
        }
    }
}
async function getDocumentContent() {
    const responseAPI = await actions.login(baseURL, payloads.loginPayload("translationReview", env));
    let token = responseAPI.data.access
    assert.equal(responseAPI.status, 200);
    
    const response = await actions.getDocumentDetails(baseURL, documentID, token);
        for (let i=0; i < response.data.subdocs.length; i++) {
            for (let j=0; j < response.data.subdocs[i].metrics.length; j++) { 
                if(response.data.subdocs[i].metrics[j].vendor ==  "AI_GENERATED"){
                    const translatedUrl = response.data.subdocs[i].metrics[j].translatedFileUrl
                    let contentResponse = await actions.getContentAPI(translatedUrl)
                    console.log(contentResponse.data)
            }
        }
    }
    assert.equal(response.status, 200);
}
// Call the function
checkXMLFilesInMarkdown();
// getDocumentContent()
