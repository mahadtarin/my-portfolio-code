import * as payloads from '../payloads';
import * as actions from '../apiActions';
const assert = require('assert');

let subdocID: string[] = [];
let token;
const env= "staging"  // Update this for your environment
const status_array = ["AWAITING_REVIEW", "AWAITING_PUBLICATION", "PUBLISHED"];
const count = 3;
const documentID = "<DOCUMENT_ID_PLACEHOLDER>";  // Replace with your document ID
const baseURL = `<API_BASE_URL>`;  // Replace with your API base URL

describe('English Source Review Portal API Automation Tests', async function () {

    it('User logs in to the English Source Review portal', async function () {
        const response = await actions.login(baseURL, payloads.loginPayload("englishReview", env));
        token = response.data.access
        assert.equal(response.status, 200);
    });
    it('User is on the English Source Review page and verifies the required documents are present in the listing', async function () {
        const response = await actions.getListingData(baseURL, token);
        assert.equal(response.status, 200);
    });

    it('User is on the English Source Review page and verifies the details for the desired document', async function () {
        const response = await actions.getDocumentDetails(baseURL, documentID, token);
        for (let i = 0; i < response.data.subdocs.length; i++) {
            subdocID.push(response.data.subdocs[i].id);
        }
        assert.equal(response.status, 200);
        assert.equal(response.data.status, status_array[0]);
        assert.equal(response.data.subdocs.length, count); 
        
    });

    it('User edits the content in the files and saves it', async function () {
        const response = await actions.editDocument(
            baseURL, 
            documentID, 
            payloads.requestBody(subdocID), 
            token
        );
        assert.equal(response.status, 200);
    });

    it('User is on the English Source Review page.', async function () {
        const response = await actions.getDocumentDetails(baseURL, documentID, token);
        assert.equal(response.status, 200);
    });

    it('User move towards verifying the next files present in the specific document', async function () {
        console.log('Total files ' + subdocID.length);
        for (let i = 0; i < (subdocID.length - 1); i++) {
            console.log('File: ' + [i + 1] + ' -> Reviewed');
            const response = await actions.editDocument(
                baseURL,
                documentID,
                payloads.nextPageRequestBody([subdocID[i]], status_array),
                token
            );
            assert.equal(response.status, 200);
            if (response.data[0].subdocs[i].id == subdocID[i]) {
                assert.equal(response.data[0].subdocs[i].status, status_array[1]);
            }
            // add a time delay of 10 seconds below;
            await new Promise(resolve => setTimeout(resolve, 10000));
        }
    });

    it('User is on the last file of the document and publishes it', async function () {
        const response = await actions.publishDocument(
            baseURL, documentID, 
            payloads.publishRequestBody([subdocID[subdocID.length - 1]], status_array), 
            token
        );
        assert.equal(response.status, 200);
        assert.equal(response.data[0].status, status_array[2]);
    });
});