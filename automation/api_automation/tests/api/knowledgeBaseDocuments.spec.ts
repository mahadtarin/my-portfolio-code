require('tsconfig-paths/register');
import fs from 'fs';
const path = require('path');
import { getAuthCookie } from '../utils/userLoginAuthentication';
import * as apiAssertions from '../utils/apiAssertions.utils';
import * as apiRequests from '../utils/apiRequests.utils';
import * as apiPaths from '../config/paths.json';
import * as knowledgeBasePayloads from '../payloads/knowledgeBasePayloads';
import * as commonPayloads from '../payloads/commonPayloads';
import assert from 'soft-assert';
import * as info from '../config/documentIngestion.json';
import * as kInfo from '../config/knowledgeBaseModel.json';
import * as pipelineConfig from "../config/pipelineConfig.json"

let id,
  chatIds:any = [],
  DocumentCount,
  token,
  search,
  embeddingId,
  vectorId,
  embeddingFunctiontype,
  ownerId,
  llmId,
  knowledgeBaseId,
  integrationId,
  conversationId,
  llmSource;
let assetId:any = [];
let Path = path.resolve(
  'tests/files/api/documentIngestion/',
  `${info.dataAseetsFile}.csv`
);
const filePath = Path.replace(/\\/g, '/');

let idPath = path.resolve(
  'tests/files/api/documentIngestion/',
  `${kInfo.idAssetFile}.csv`
);
const idFilePath = idPath.replace(/\\/g, '/');

describe('Verify Read csv_Document Knowledge Base Model flow', async () => {
  it('log in to DPS to get cookie', async () => {
    token = await getAuthCookie();
  });
  it('Get pre requisites to create the Knowledge Base Model', async () => {
    let getEmbeddingIdData = await apiRequests.getRequest(
      apiPaths['KnowledgeBase-Services'].getEmbeddingId,
      token
    );
    embeddingId = getEmbeddingIdData['Data'].data[0].id;
    console.log("embeddingFunctionId: ",embeddingId)
    embeddingFunctiontype = getEmbeddingIdData['Data'].data[0].type;

    apiAssertions.verifyStatusCode(
      getEmbeddingIdData['Status'],
      200,
      apiPaths['KnowledgeBase-Services'].getEmbeddingId
    );
    let getIntegrationIdData = await apiRequests.getRequest(
      apiPaths['KnowledgeBase-Services'].getIntegrationId,
      token
    );
    for (var i=0; i<(getIntegrationIdData['Data'].data).length; i++)
    {
      if (getIntegrationIdData['Data'].data[i].name === process.env.VECTOR_STORE_NAME || "Vector Store")
      {
        integrationId = getIntegrationIdData['Data'].data[i].id
        console.log("IntegrationId: ",integrationId)
      }
    }
    apiAssertions.verifyStatusCode(
      getIntegrationIdData['Status'],
      200,
      apiPaths['KnowledgeBase-Services'].getIntegrationId
    );
    let getVectorIdData = await apiRequests.getRequest(
      `${apiPaths['KnowledgeBase-Services'].getvectorId}${integrationId}/integrations/`,
      token
    );

    vectorId = getVectorIdData['Data'].data.result[0].id;
    console.log("vectorId: ",vectorId)
    apiAssertions.verifyStatusCode(
      getVectorIdData['Status'],
      200,
      `${apiPaths['KnowledgeBase-Services'].getvectorId}${integrationId}/integrations/`
    );
  });
  it.skip('Unable to configure source error should upon trying to configure the model without custom source name', async () => {
    let actualName;
    let data = knowledgeBasePayloads.createKnowledgeBasePayload(
      '',
      embeddingId,
      vectorId,
      kInfo.description,
      kInfo.documentOverlapSize,
      kInfo.documentSplitSize
    );
    let inputcredentials = await apiRequests.postRequest(
      apiPaths['KnowledgeBase-Services'].sendKnowledgeData,
      token,
      data
    );
    actualName = inputcredentials['Data'].name;

    apiAssertions.verifyStatusCode(
      inputcredentials['Status'],
      400,
      apiPaths['KnowledgeBase-Services'].sendKnowledgeData
    );
    apiAssertions.verifyValueMatches(
      actualName,
      kInfo.modelName,
      `Expected: ${kInfo.modelName} Actual : ${actualName}
            Configuring without name`
    );
  });
  it.skip('Unable to configure source error should upon trying to configure the model with special characters', async () => {
    let actualName;
    let data = knowledgeBasePayloads.createKnowledgeBasePayload(
      '@@@',
      embeddingId,
      vectorId,
      kInfo.description,
      kInfo.documentOverlapSize,
      kInfo.documentSplitSize
    );
    let inputcredentials = await apiRequests.postRequest(
      apiPaths['KnowledgeBase-Services'].sendKnowledgeData,
      token,
      data
    );
    actualName = inputcredentials['Data'].name;
    apiAssertions.verifyStatusCode(
      inputcredentials['Status'],
      400,
      apiPaths['KnowledgeBase-Services'].sendKnowledgeData
    );
    apiAssertions.verifyValueMatches(
      actualName,
      kInfo.modelName,
      `Expected: ${kInfo.modelName} Actual : ${actualName}
            Configuring with special characters`
    );
  });
  it('Configure the required information for the Knowledge Base Model', async () => {
    let actualStatus,
      actualembeddingId,
      actualvectorId,
      actualName,
      actualDescription,
      actualSplitSize,
      actualDocumentOverlapSize;
    let data = knowledgeBasePayloads.createKnowledgeBasePayload(
      kInfo.modelName,
      embeddingId,
      vectorId,
      kInfo.description,
      kInfo.documentOverlapSize,
      kInfo.documentSplitSize
    );
    let inputcredentials = await apiRequests.postRequest(
      apiPaths['KnowledgeBase-Services'].sendKnowledgeData,
      token,
      data
    );
    actualName = inputcredentials['Data'].data.name;
    actualDescription = inputcredentials['Data'].data.description;
    knowledgeBaseId = inputcredentials['Data'].data.id;
    actualStatus = inputcredentials['Data'].status;
    actualvectorId = inputcredentials['Data'].data.vectorStoreIntegrationId;
    actualembeddingId = inputcredentials['Data'].data.embeddingFunctionId;
    actualSplitSize = inputcredentials['Data'].data.documentSplitSize;
    actualDocumentOverlapSize = inputcredentials['Data'].data.documentOverlapSize;
    ownerId = inputcredentials['Data'].data.ownerId;

    apiAssertions.verifyStatusCode(
      inputcredentials['Status'],
      200,
      apiPaths['KnowledgeBase-Services'].sendKnowledgeData
    );
    apiAssertions.verifyValueMatches(
      actualStatus,
      'success',
      `Expected success: success Actual success: ${actualStatus}
            While adding inputs`
    );
    apiAssertions.verifyValueMatches(
      actualembeddingId,
      embeddingId,
      `Expected embeddingId: ${embeddingId} Actual embeddingId: ${actualembeddingId}
            While adding inputs`
    );
    apiAssertions.verifyValueMatches(
      actualvectorId,
      vectorId,
      `Expected vectorId: ${vectorId} Actual vectorId: ${actualvectorId}
            While adding inputs`
    );
    apiAssertions.verifyValueMatches(
      actualName,
      kInfo.modelName,
      `Expected: ${kInfo.modelName} Actual : ${actualName}
            While adding inputs`
    );
    apiAssertions.verifyValueMatches(
      actualDescription,
      kInfo.description,
      `Expected description: ${kInfo.description} Actual description: ${actualDescription}
            While adding inputs`
    );
    apiAssertions.verifyValueMatches(
      actualDocumentOverlapSize,
      kInfo.documentOverlapSize,
      `Expected Document overlap size : ${kInfo.documentOverlapSize} Actual Document overlap size : ${actualDocumentOverlapSize}`
    );
    apiAssertions.verifyValueMatches(
      actualSplitSize,
      kInfo.documentSplitSize,
      `Expected Document split size : ${kInfo.documentSplitSize} Actual Document split size : ${actualSplitSize}`
    );
  });
  it('Verify the draft status with no Source Document attached ', async () => {
    let actualStatus, actualDocument, actualName, actualDescription, actualType;
    let onListPage = await apiRequests.getRequest(
      apiPaths['KnowledgeBase-Services'].KnowledgeBaseListing,
      token
    );
    for (let i = 0; i < onListPage['Data'].data.result.length; i++) {
      if (onListPage['Data'].data.result[i].id == knowledgeBaseId) {
        actualName = onListPage['Data'].data.result[i].name;
        actualDescription = onListPage['Data'].data.result[i].description;
        actualType = onListPage['Data'].data.result[i].embeddingFunction.type;
        actualStatus = onListPage['Data'].data.result[i].status;
        break;
      }
    }
    apiAssertions.verifyStatusCode(
      onListPage['Status'],
      200,
      apiPaths['KnowledgeBase-Services'].KnowledgeBaseListing
    );
    apiAssertions.verifyValueMatches(
      actualStatus,
      'draft',
      `Expected status: draft Actual status: ${actualStatus}
                While checking source draft status`
    );
    apiAssertions.verifyValueMatches(
      actualDocument,
      {},
      `Expected document: ${{}} Actual document: ${actualDocument}
                While checking source draft status`
    );
    apiAssertions.verifyValueMatches(
      actualName,
      kInfo.modelName,
      `Expected name: ${kInfo.modelName} Actual name: ${actualName}
                While checking source draft status`
    );
    apiAssertions.verifyValueMatches(
      actualType,
      embeddingFunctiontype,
      `Expected function type: ${embeddingFunctiontype} Actual function type: ${actualType}
                While checking source draft status`
    );
    apiAssertions.verifyValueMatches(
      actualDescription,
      kInfo.description,
      `Expected description: ${kInfo.description} Actual description: ${actualDescription}
                    While checking source draft status`
    );
  });
  it('Search and select the Source for the Knowledge Base Model', async () => {
    let namesArray,actualDestination,actualSyncFrequency,actualSourceName,actualCustomSourceName;
    let data = fs.readFileSync(filePath, 'utf8');
    const lines = data.trim().split('\n');
    namesArray = lines.map(line => line.replace(/"/g, '').trim());
    DocumentCount = namesArray.length;

    for (let i = 0; i < DocumentCount; i++) {
      search = namesArray[i];
      let actualStatus, actualName, actualTransformationType;
      let searchSource = commonPayloads.dataCatalougeListingFilter(search);
      let selectSource = await apiRequests.postRequest(
        apiPaths['Asset-Service'].dataCatalougePageFilter,
        token,
        searchSource
      );
      
      actualStatus = selectSource['Data'].status;
      actualDestination = selectSource['Data'].data.result[0].destinations
      actualSyncFrequency = selectSource['Data'].data.result[0].syncFrequency
      actualSourceName= selectSource['Data'].data.result[0].sourceDetails[0].sourceName
      actualCustomSourceName = selectSource['Data'].data.result[0].sourceDetails[0].customSourceName
      assetId.push(selectSource['Data'].data.result[0].assetID);
      actualName = selectSource['Data'].data.result[0].name;
      actualTransformationType =
        selectSource['Data'].data.result[0].transformationType;
      
      apiAssertions.verifyStatusCode(
        selectSource['Status'],
        200,
        apiPaths['Asset-Service'].dataCatalougePageFilter
      );
      apiAssertions.verifyValueMatches(
        actualStatus,
        'success',
        `Expected success: success Actual success: ${actualStatus}
                In data catalogue Page`
      );
      apiAssertions.verifyValueMatches(
        actualDestination,
        process.env.EXPECTED_S3_DESTINATION || "s3-destination-name",
        `Expected ${process.env.EXPECTED_S3_DESTINATION || "s3-destination-name"} Actual  ${actualDestination}
                In data catalogue Page`
      );
      apiAssertions.verifyValueMatches(
        actualSyncFrequency,
        'manual',
        `Expected : manual Actual : ${actualSyncFrequency}
                In data catalogue Page`
      );
      apiAssertions.verifyValueMatches(
        actualSourceName,
        'Documents',
        `Expected : Documents Actual success: ${actualSourceName}
                In data catalogue Page`
      );
      apiAssertions.verifyValueMatches(
        actualName,
        search,
        `Expected name: ${search} Actual name: ${actualName}
                In data catalogue Page`
      );
      apiAssertions.verifyValueMatches(
        actualTransformationType,
        'collection',
        `Expected: type Actual type: ${actualTransformationType}
                In data catalogue Page`
      );
    }
  });
  it('Add the data source to the Knowledge Base Model', async () => {
    let actualStatus, actualvectorId, actualembeddingId, actualOwnerId;
    let data = knowledgeBasePayloads.createAddDocumentPayLoad(
      kInfo.modelName,
      embeddingId,
      vectorId,
      kInfo.description,
      assetId
    );
    let addSource = await apiRequests.putRequest(
      `${apiPaths['KnowledgeBase-Services'].sendKnowledgeData}${knowledgeBaseId}/?is_publish=false`,
      token,
      data
    );
    id = addSource['Data'].data.id;
    console.log(addSource['Data'].data);
    fs.writeFile(idFilePath, `${id}`, err => {
      if (err) throw err;
    });
    actualStatus = addSource['Data'].data.status;
    actualvectorId = addSource['Data'].data.vectorStoreIntegrationId;
    actualembeddingId = addSource['Data'].data.embeddingFunctionId;
    actualOwnerId = addSource['Data'].data.ownerId;

    apiAssertions.verifyStatusCode(
      addSource['Status'],
      200,
      `${apiPaths['KnowledgeBase-Services'].sendKnowledgeData}${knowledgeBaseId}/?is_publish=false`
    );
    apiAssertions.verifyValueMatches(
      actualembeddingId,
      embeddingId,
      `Expected embeddingId: ${embeddingId} Actual embeddingId: ${actualembeddingId}
            While adding source`
    );
    apiAssertions.verifyValueMatches(
      actualvectorId,
      vectorId,
      `Expected vectorId: ${vectorId} Actual vectorId: ${actualvectorId}
            While adding source`
    );
    apiAssertions.verifyValueMatches(
      actualStatus,
      'draft',
      `Expected status: draft Actual status: ${actualStatus}
            While adding source`
    );

    apiAssertions.verifyValueMatches(
      actualOwnerId,
      ownerId,
      `Expected ownerId: ${ownerId} Actual ownerId: ${actualOwnerId}
            While adding source`
    );
  });
  it('Verify the draft status with Source Document attached ', async () => {
    let interval = 20000;
    await new Promise(resolve => setTimeout(resolve, interval));
    let actualStatus,
      actualDocument,
      actualName,
      actualDescription,
      actualType,
      actualDocumentCount;
    let onListPage = await apiRequests.getRequest(
      apiPaths['KnowledgeBase-Services'].KnowledgeBaseListing,
      token
    );
    for (var i = 0; i < onListPage['Data'].data.result.length; i++) {
      if (onListPage['Data'].data.result[i].id === knowledgeBaseId) {
        actualName = onListPage['Data'].data.result[i].name;
        actualDescription = onListPage['Data'].data.result[i].description;
        actualType = onListPage['Data'].data.result[i].embeddingFunction.type;
        actualStatus = onListPage['Data'].data.result[i].status;
        actualDocument = onListPage['Data'].data.result[i].knowledgeBaseAssets[0].transformationType;
        actualDocumentCount = onListPage['Data'].data.result[i].knowledgeBaseAssets.length;
        break;
      }
    }
    apiAssertions.verifyValueMatches(
      actualName,
      kInfo.modelName,
      `Expected name: ${kInfo.modelName} Actual name: ${actualStatus}
                    At listing Page`
    );
    apiAssertions.verifyValueMatches(
      actualStatus,
      'draft',
      `Expected status: draft Actual status: ${actualStatus}
                    At listing Page`
    );
    apiAssertions.verifyValueMatches(
      actualDocument,
      'collection',
      `Expected type: collection Actual type: ${actualDocument}
                    At listing Page`
    );
    apiAssertions.verifyValueMatches(
      actualDocumentCount,
      DocumentCount,
      `Expected count: ${DocumentCount} Actual count: ${actualDocumentCount}
                    At listing Page`
    );
    apiAssertions.verifyValueMatches(
      actualType,
      embeddingFunctiontype,
      `Expected function type: ${embeddingFunctiontype} Actual function type: ${actualType}
                    At listing Page`
    );
    apiAssertions.verifyValueMatches(
      actualDescription,
      kInfo.description,
      `Expected description: ${kInfo.description} Actual description: ${actualDescription}
                    At listing Page`
    );
  });
  it('Verify the not_learned status of the source', async () => {
    let actualStatus;
    let notLearnStatus = await apiRequests.getRequest(
      apiPaths['KnowledgeBase-Services'].KnowledgeBaseListing,
      token
    );
    apiAssertions.verifyStatusCode(
      notLearnStatus['Status'],
      200,
      apiPaths['KnowledgeBase-Services'].KnowledgeBaseListing
    );
    for (var i = 0; i < notLearnStatus['Data'].data.result.length; i++) {
      if (notLearnStatus['Data'].data.result[i].id === knowledgeBaseId) {
        for (
          var j = 0;
          j < notLearnStatus['Data'].data.result[i].knowledgeBaseAssets.length;
          j++
        ) {
          actualStatus =
          notLearnStatus['Data'].data.result[i].knowledgeBaseAssets[j].status;
          console.log(actualStatus);
          apiAssertions.verifyValueMatches(
            actualStatus,
            'not_learned',
            `Expected status: learned Actual status: ${actualStatus}
                    While checking status`
          );
        }
      }
    }
  });
  it('Verify the learning status of the source', async () => {
    let actualStatus;
    let data1 = knowledgeBasePayloads.learningStatusPayload(knowledgeBaseId);
    let embedding = await apiRequests.postRequest(
      apiPaths['KnowledgeBase-Services'].embeddings,
      token,
      data1
    );
    apiAssertions.verifyStatusCode(
      embedding['Status'],
      200,
      apiPaths['KnowledgeBase-Services'].embeddings
    );
    let interval = 20000;
    await new Promise(resolve => setTimeout(resolve, interval));
    let learnStatus = await apiRequests.getRequest(
      apiPaths['KnowledgeBase-Services'].KnowledgeBaseListing,
      token
    );
    apiAssertions.verifyStatusCode(
      learnStatus['Status'],
      200,
      apiPaths['KnowledgeBase-Services'].KnowledgeBaseListing
    );
    for (var i = 0; i < learnStatus['Data'].data.result.length; i++) {
      if (learnStatus['Data'].data.result[i].id === knowledgeBaseId) {
        for (
          var j = 0;
          j < learnStatus['Data'].data.result[i].knowledgeBaseAssets.length;
          j++
        ) {
          actualStatus =
            learnStatus['Data'].data.result[i].knowledgeBaseAssets[j].status;
          console.log(actualStatus);
          apiAssertions.verifyValueMatches(
            actualStatus,
            'learning',
            `Expected status: learning Actual status: ${actualStatus}
                        While Checking Status`
          );
        }
      }
    }
    let interval1 = 10000;
    await new Promise(resolve => setTimeout(resolve, interval1));
  });
  it('Get the LLM ID that will be used to send prompt', async () => {
    llmSource = await apiRequests.getRequest(
      apiPaths['KnowledgeBase-Services'].llmModel,
      token
    );
    llmId = llmSource['Data'].data[0].id;
  });
  it('Send the message to Author for testing the model', async () => {
    let data = knowledgeBasePayloads.createTestSourcePayload(
      process.env.TEST_PROMPT || 'What can you tell me about this knowledge base?',
      llmId,
      knowledgeBaseId,
      kInfo.temperature,
      kInfo.penalty,
      kInfo.responseLength
    );
    let actualMessage = await apiRequests.getStreamingData(
      `${apiPaths['KnowledgeBase-Services'].testSourceModel}${data}`,
      token
    );
    conversationId = actualMessage.data.conversation_id
    console.log("Conversation Id: ",conversationId)
    function check() {
      if (actualMessage.data.content.length > 5) return true;
    }
    apiAssertions.verifyValueMatches(
      check(),
      true,
      `Expected: ${true} Actual : ${check()}`
    );
  });
  it('Send another message with different parameters', async () => {
      let data = knowledgeBasePayloads.createTestSourcePayload(
        kInfo.prompt,
        llmId,
        knowledgeBaseId,
        0.5,
        0.5,
        1048
      );
      let actualMessage = await apiRequests.getStreamingData(
        `${apiPaths['KnowledgeBase-Services'].testSourceModel}${data}`,
        token
      );
      function check() {
        if (actualMessage.data.content.length > 5) return true;
      }
      apiAssertions.verifyValueMatches(
        check(),
        true,
        `Expected: ${true} Actual : ${check()}`
      );
  });
  it('Get the required message ids that will be used to save prompt', async () => {
    let getIds = await apiRequests.getRequest(
      `${apiPaths['Data-Products'].getConversation}${conversationId}/`,
      token
    );
    for (var i=0; i<(getIds['Data'].data).length; i++)
    {
      if(i%2 === 0)
      {
        chatIds.push(getIds['Data'].data[i].id)
      }
    }
    apiAssertions.verifyStatusCode(
      getIds['Status'],
      200,
      `${apiPaths['Data-Products'].getConversation}${conversationId}`
    );
  });
  it('Save the prompt', async () => {
    for (var i=0;i<chatIds.length;i++)
    {
      let savePrompt = await apiRequests.patchRequest(
        `${apiPaths['Data-Products'].getConversation}${conversationId}/messages/${chatIds[i]}/?is_prompt=true`,
        token
      );
      apiAssertions.verifyStatusCode(
        savePrompt['Status'],
        200,
        `${apiPaths['Data-Products'].getConversation}${conversationId}/messages/${chatIds[i]}/?is_prompt=true`
      );
    }
  });
  it('Verify the prompt is saved', async () => {
    let actualContent;
    let data = knowledgeBasePayloads.saveChatPayload(knowledgeBaseId);
    let verifyPrompt = await apiRequests.postRequest(
      apiPaths['KnowledgeBase-Services'].prompts,
      token,
      data
    );
    apiAssertions.verifyStatusCode(
      verifyPrompt['Status'],
      200,
      apiPaths['KnowledgeBase-Services'].prompts
    );
    for (var i=0;i<verifyPrompt['Data'].data; i++)
    {
      actualContent = verifyPrompt['Data'].data[i].content
      apiAssertions.verifyValueMatches(
        actualContent,
        kInfo.prompt[i],
        `Expected: ${kInfo.prompt[i]} Actual : ${actualContent}
              While Saving Chat`
      );
    }
  });
  it('Delete the prompt', async () => {
    for (var i=0;i<chatIds.length;i++)
    {
      let deletePrompt = await apiRequests.patchRequest(
        `${apiPaths['Data-Products'].getConversation}${conversationId}/messages/${chatIds[i]}/?is_prompt=false`,
        token
      );
      apiAssertions.verifyStatusCode(
        deletePrompt['Status'],
        200,
        `${apiPaths['Data-Products'].getConversation}${conversationId}/messages/${chatIds[i]}/?is_prompt=false`
      );
    }
  });
  it('Verify the prompts is deleted', async () => {
    let data = knowledgeBasePayloads.saveChatPayload(knowledgeBaseId);
    let verifyPrompt = await apiRequests.postRequest(
      apiPaths['KnowledgeBase-Services'].prompts,
      token,
      data
    );
    console.log(verifyPrompt['Data'].data)
    apiAssertions.verifyStatusCode(
      verifyPrompt['Status'],
      200,
      apiPaths['KnowledgeBase-Services'].prompts
    );
    apiAssertions.verifyValueMatches(
      verifyPrompt['Data'].data,
      [],
      `Expected: [] Actual : ${verifyPrompt['Data'].data}
          Verifying Chat is Deleted`
    );
  });
  it('Save the prompt', async () => {
    for (var i=0;i<chatIds.length;i++)
    {
      let chatData = await apiRequests.patchRequest(
        `${apiPaths['Data-Products'].getConversation}${conversationId}/messages/${chatIds[i]}/?is_prompt=true`,
        token
      );
      apiAssertions.verifyStatusCode(
        chatData['Status'],
        200,
        `${apiPaths['Data-Products'].getConversation}${conversationId}/messages/${chatIds[i]}/?is_prompt=true`
      );
    }
  });
  it('Complete the drafting state of knowledge base and move to review page step', async () => {
    let data = knowledgeBasePayloads.createCompleteKnowledgeBasePayload(
      kInfo.modelName,
      embeddingId,
      vectorId,
      kInfo.description,
      assetId
    );
    let completeTestPageResponse = await apiRequests.putRequest(
      `${apiPaths['KnowledgeBase-Services'].sendKnowledgeData}${knowledgeBaseId}/?is_publish=false`,
      token,
      data
    );
    apiAssertions.verifyStatusCode(
      completeTestPageResponse['Status'],
      200,
      `${apiPaths['KnowledgeBase-Services'].sendKnowledgeData}${knowledgeBaseId}/?is_publish=false`
    );
  });
  it('Verify the information on review Page', async () => {
    let actualKbId, actualName, actualDescription, actualFunction;
    let reviewInfo = await apiRequests.getRequest(
      `${apiPaths['KnowledgeBase-Services'].sendKnowledgeData}${knowledgeBaseId}/`,
      token
    );

    actualKbId = reviewInfo['Data'].data.id;
    actualName = reviewInfo['Data'].data.name;
    actualDescription = reviewInfo['Data'].data.description;
    actualFunction = reviewInfo['Data'].data.embeddingFunction.type;

    apiAssertions.verifyStatusCode(
      reviewInfo['Status'],
      200,
      `${apiPaths['KnowledgeBase-Services'].sendKnowledgeData}${knowledgeBaseId}/`
    );
    apiAssertions.verifyValueMatches(
      actualKbId,
      knowledgeBaseId,
      `Expected knowledgeBase Id: ${knowledgeBaseId} Actual knowledgeBase Id: ${actualKbId}
            At review Page`
    );
    apiAssertions.verifyValueMatches(
      actualName,
      kInfo.modelName,
      `Expected name: ${kInfo.modelName} Actual name: ${actualName}
            At review Page`
    );
    apiAssertions.verifyValueMatches(
      actualDescription,
      kInfo.description,
      `Expected description: ${kInfo.description} Actual description: ${actualDescription}
            At review Page`
    );
    apiAssertions.verifyValueMatches(
      actualFunction,
      embeddingFunctiontype,
      `Expected function type: ${embeddingFunctiontype} Actual function type: ${actualFunction}
            At review Page`
    );
  });
  it('Publish with the Source to be Knoledge Base Model', async () => {
    let actualStatus, actualvectorId, actualembeddingId, actualOwnerId;
    let data = knowledgeBasePayloads.createKnowledgeBasePayload(
      kInfo.modelName,
      embeddingId,
      vectorId,
      kInfo.description,
      kInfo.documentOverlapSize,
      kInfo.documentSplitSize
    );
    let publishSource = await apiRequests.putRequest(
      `${apiPaths['KnowledgeBase-Services'].sendKnowledgeData}${knowledgeBaseId}/?is_publish=true`,
      token,
      data
    );
    actualStatus = publishSource['Data'].data.status;
    actualvectorId = publishSource['Data'].data.vectorStoreIntegrationId;
    actualembeddingId = publishSource['Data'].data.embeddingFunctionId;
    actualOwnerId = publishSource['Data'].data.ownerId;

    apiAssertions.verifyStatusCode(
      publishSource['Status'],
      200,
      `${apiPaths['KnowledgeBase-Services'].sendKnowledgeData}${knowledgeBaseId}/?is_publish=true`
    );
    apiAssertions.verifyValueMatches(
      actualembeddingId,
      embeddingId,
      `Expected embeddingId: ${embeddingId} Actual embeddingId: ${actualembeddingId}
            After Publishing`
    );
    apiAssertions.verifyValueMatches(
      actualvectorId,
      vectorId,
      `Expected vectorId: ${vectorId} Actual vectorId: ${actualvectorId}
            After Publishing`
    );
    apiAssertions.verifyValueMatches(
      actualStatus,
      'published',
      `Expected status: learned Actual status: ${actualStatus}
            After Publishing`
    );

    apiAssertions.verifyValueMatches(
      actualOwnerId,
      ownerId,
      `Expected ownerId: ${ownerId} Actual ownerId: ${actualOwnerId}
            After Publishing`
    );
    let interval = 20000;
    await new Promise(resolve => setTimeout(resolve, interval));
  });
  it('Verify the published status with Source Document attached', async () => {
    let actualStatus,
      actualDocument,
      actualName,
      actualDescription,
      actualType,
      actualDocumentCount;
    let onListPage = await apiRequests.getRequest(
      apiPaths['KnowledgeBase-Services'].KnowledgeBaseListing,
      token
    );
    for (var i = 0; i < onListPage['Data'].data.result.length; i++) {
      if (onListPage['Data'].data.result[i].id == knowledgeBaseId) {
        actualName = onListPage['Data'].data.result[i].name;
        actualDescription = onListPage['Data'].data.result[i].description;
        actualType = onListPage['Data'].data.result[i].embeddingFunction.type;
        actualStatus = onListPage['Data'].data.result[i].status;
        actualDocument =
        onListPage['Data'].data.result[i].knowledgeBaseAssets[0]
            .transformationType;
        actualDocumentCount =
        onListPage['Data'].data.result[i].knowledgeBaseAssets.length;
        break;
      }
    }
    apiAssertions.verifyStatusCode(
      onListPage['Status'],
      200,
      apiPaths['KnowledgeBase-Services'].KnowledgeBaseListing
    );
    apiAssertions.verifyValueMatches(
      actualName,
      kInfo.modelName,
      `Expected name: ${kInfo.modelName} Actual name: ${actualStatus}
                    At listing Page`
    );
    apiAssertions.verifyValueMatches(
      actualStatus,
      'published',
      `Expected status: published Actual status: ${actualStatus}
                    At listing Page`
    );
    apiAssertions.verifyValueMatches(
      actualDocument,
      'collection',
      `Expected type: collection Actual type: ${actualDocument}
                    At listing Page`
    );
    apiAssertions.verifyValueMatches(
      actualDocumentCount,
      DocumentCount,
      `Expected count: ${DocumentCount} Actual count: ${actualDocumentCount}
                    At listing Page`
    );
    apiAssertions.verifyValueMatches(
      actualType,
      embeddingFunctiontype,
      `Expected function type: ${embeddingFunctiontype} Actual function type: ${actualType}
                    At listing Page`
    );
    apiAssertions.verifyValueMatches(
      actualDescription,
      kInfo.description,
      `Expected description: ${kInfo.description} Actual description: ${actualDescription}
                    At listing Page`
    );

    assert.softAssertAll();
  });
});
