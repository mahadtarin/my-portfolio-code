import http from "k6/http";
import { sleep, check } from "k6";
const knowledgeAgentConfig = require(`../config/benchmarkingConfig.js`);

// Global configuration
const apiBaseUrl = process.env.API_BASE_URL || 'https://app.your-domain.com';

let servingTypePayload = [];
let productID;
let dataProductName;
let domainIDs, userIDs;
let servingPayload = [];

export function getServingTypeUpdated(cookie) {
  const headers = { 
    'accept': 'application/json', 
    'accept-language': 'en-US,en;q=0.9', 
    'cache-control': 'no-cache', 
    'cookie': `${cookie}`
  };
  
  const apiBaseUrl = process.env.API_BASE_URL || 'https://app.your-domain.com';
  let response = http.get(`${apiBaseUrl}/data-products/api/v1/products/serving/`, { headers: headers });
  let servingTypes = JSON.parse(response.body);

  for (let l = 0; l < (servingTypes.data.length); l++) {
    if (servingTypes.data[l].label === "Knowledge Agent") {
      servingPayload.push(servingTypes.data[l]);
      break;
    }
  }
  
   servingPayload.map(item => {
    item.supportedSubServings = item.supportedSubServings.filter(subServing => subServing.label === 'Chat with your Datasets');
    return item;
  });

  // Check response
  check(response, {
    'Successfully fetched serving types': (r) => r.status === 200 && servingPayload.length > 0
  });
}

export function selectServingTypeUpdated(cookie) {
  let payload = JSON.stringify({
    draftingStatus: {
      '1': true,
      '2': false,
      '3': false,
      '4': false,
      '5': false,
      '6': false,
    },
    dataProductStatus: "draft",
    servings: servingPayload,
    dataDomain: "sales",
  });

  const headers = { 
    'accept': 'application/json', 
    'accept-language': 'en-US,en;q=0.9', 
    'cache-control': 'no-cache', 
    'cookie': `${cookie}`
  };
  
  let response = http.post(`${apiBaseUrl}/data-products/api/v1/products/`, payload, { headers: headers });
  let createDataProduct = JSON.parse(response.body);
  productID = createDataProduct.data.productID;

  // Check response
  check(response, {
    'Successfully selected serving type': (r) => r.status === 201 && productID !== undefined
  });
}

export function addDataProductOverview(cookie) {

  const timestamp = new Date().getTime();
  dataProductName = `benchmark_${timestamp}_${Math.floor(Math.random() * 10000).toString().padStart(3, '0')}`;

  let payload = JSON.stringify({
    name: dataProductName,
    description: knowledgeAgentConfig.knowledgeAgent.description,
    dataProductStatus: "status",
    draftingStatus: {
      '1': true,
      '2': true,
      '3': false,
      '4': false,
      '5': false,
      '6': false,
    },
    servings: servingPayload
  });

  const headers = { 
    'accept': 'application/json', 
    'accept-language': 'en-US,en;q=0.9', 
    'cache-control': 'no-cache', 
    'cookie': `${cookie}`
  };

  let response = http.put(`${apiBaseUrl}/data-products/api/v1/products/${productID}/`, payload, { headers: headers });

  // Check response
  check(response, {
    'Successfully added data product overview': (r) => r.status === 200
  });
}

export function addDataset(cookie) {
  let payload = JSON.stringify({
    newAssets: [],
    removeAssets: [],
    newKnowledgeBases: ["19a010ac-fbb6-4d8a-859f-1e8e40f1b4d2"],
    removeKnowledgeBases: [],
  });

  const headers = { 
    'accept': 'application/json', 
    'accept-language': 'en-US,en;q=0.9', 
    'cache-control': 'no-cache', 
    'cookie': `${cookie}`
  };

  let response = http.post(`${apiBaseUrl}/data-products/api/v1/products/${productID}/add-assets/`, payload, { headers: headers });

  // Check response
  check(response, {
    'Successfully added dataset': (r) => r.status === 200
  });
}

export function completeDataCatalogueStep(cookie) {
  let payload = JSON.stringify({
    "productID": productID,
    "isNewUi": false,
    "name": dataProductName,
    "dataDomain": process.env.DATA_DOMAIN || "sales",
    "description": knowledgeAgentConfig.knowledgeAgent.description,
    "dataProductStatus": "draft",
    "owner": parseInt(process.env.OWNER_ID) || 191,
    "connectedApp": null,
    "domainOwners": null,
    "workspaceId": parseInt(process.env.WORKSPACE_ID) || 67,
    "draftingStatus": {
      "1": true,
      "2": true,
      "3": true,
      "4": false,
      "5": false,
      "6": false
    }
  });

  const headers = { 
    'cookie': `${cookie}`
  };

  let response = http.put(`${apiBaseUrl}/data-products/api/v1/products/${productID}/`, payload, { headers: headers });
  // Check response
  check(response, {
    'Successfully completed data catalogue step': (r) => r.status === 200
  });
}

export function completeDataServingStep(cookie) {
  const timestamp = new Date().getTime();
  let payload = JSON.stringify({
    productID: productID,
    isNewUi: true,
    name: dataProductName,
    dataDomain: process.env.DATA_DOMAIN || "sales",
    description: knowledgeAgentConfig.knowledgeAgent.description,
    dataProductStatus: 'draft',
    owner: parseInt(process.env.OWNER_ID) || 191,
    domainOwners: null,
    workspaceId: parseInt(process.env.WORKSPACE_ID) || 67,
    draftingStatus: {
      '1': true,
      '2': true,
      '3': true,
      '4': true,
      '5': false,
      '6': false
    }
  });

  const headers = { 
    'accept': 'application/json', 
    'accept-language': 'en-US,en;q=0.9', 
    'cache-control': 'no-cache', 
    'cookie': `${cookie}`
  };

  let response = http.put(`${apiBaseUrl}/data-products/api/v1/products/${productID}/`, payload, { headers: headers });

  // Check response
  check(response, {
    'Successfully completed data serving step': (r) => r.status === 200
  });
}

export function addGovernance(cookie) {
  let payload = JSON.stringify({
    chatbotServing: {
      modelParameters: {
        temperature: 0.7,
        responseLength: 2048,
        similaritySearchThreshold: 0.6,
        penalty: 1.5,
        llmModelId: process.env.LLM_MODEL_ID || "your-llm-model-id",
      },
      enableApi: true,
    }
  });

  const headers = { 
    'accept': 'application/json', 
    'accept-language': 'en-US,en;q=0.9', 
    'cache-control': 'no-cache', 
    'cookie': `${cookie}`
  };

  // Serve data product endpoint (commented out for this demo)
  // let response = http.post(`${apiBaseUrl}/data-products/api/v1/products/${productID}/serve/?dashboardID=`, payload, { headers: headers });
  sleep(5);
  // Fetch user and domain IDs (commented out for this demo)
  // let userResponse = http.get(`${apiBaseUrl}/auth-service-keycloak/api/v1/workspaces/users/?limit=25&offset=0&search=`, { headers: headers }); 
  // let getInfo = JSON.parse(userResponse.body);
  // userIDs = getInfo.data.result[0].user.id;
  // domainIDs = getInfo.data.result[0].user.domainID;

  // Check responses
  // check(response, {
  //   'Successfully added governance': (r) => r.status === 200
  // });

  // check(userResponse, {
  //   'Successfully fetched user info': (r) => r.status === 200 && userIDs !== undefined && domainIDs !== undefined
  // });
}

export function completeGovernanceStep(cookie) {
  const headers = { 
    'accept': 'application/json', 
    'accept-language': 'en-US,en;q=0.9', 
    'cache-control': 'no-cache', 
    'cookie': `${cookie}`
  };

  let payload1 = JSON.stringify({
    domainIDs: [parseInt(process.env.DOMAIN_ID) || 52],
    userIDs: [parseInt(process.env.OWNER_ID) || 191],
  });

  let response1 = http.post(`${apiBaseUrl}/data-products/api/v1/products/${productID}/governance/`, payload1, { headers: headers });
  
  const timestamp = new Date().getTime();
  let payload = JSON.stringify({
    productID: productID,
    isNewUi: true,
    name: dataProductName,
    dataDomain: process.env.DATA_DOMAIN || "sales",
    description: knowledgeAgentConfig.knowledgeAgent.description,
    dataProductStatus: 'draft',
    owner: parseInt(process.env.OWNER_ID) || 191,
    domainOwners: null,
    workspaceId: parseInt(process.env.WORKSPACE_ID) || 67,
    draftingStatus: {
      '1': true,
      '2': true,
      '3': true,
      '4': true,
      '5': true,
      '6': false
    }
  });

  let response2 = http.put(`${apiBaseUrl}/data-products/api/v1/products/${productID}/`, payload, { headers: headers });

  // Check responses
  check(response1, {
    'Successfully completed governance step': (r) => r.status === 200
  });

  check(response2, {
    'Successfully updated data product': (r) => r.status === 200
  });
}

export function publishDataProduct(cookie) {
  let payload = JSON.stringify({
    productID: productID,
    isNewUi: true,
    name: dataProductName,
    dataDomain: process.env.DATA_DOMAIN || "sales",
    description: knowledgeAgentConfig.knowledgeAgent.description,
    dataProductStatus: 'completed',
    workspaceId: parseInt(process.env.WORKSPACE_ID) || 67,
    draftingStatus: {
      '1': true,
      '2': true,
      '3': true,
      '4': true,
      '5': true,
      '6': true,
    }
  });

  const headers = { 
    'accept': 'application/json', 
    'accept-language': 'en-US,en;q=0.9', 
    'cache-control': 'no-cache', 
    'cookie': `${cookie}`
  };

  let response = http.put(`${apiBaseUrl}/data-products/api/v1/products/${productID}/`, payload, { headers: headers });

  // Check response
  check(response, {
    'Successfully published data product': (r) => r.status === 200
  });
}
