import http from "k6/http";
import { check } from 'k6';
import { htmlReport } from "https://raw.githubusercontent.com/benc-uk/k6-reporter/2.2.0/dist/bundle.js"; 
import { getAuthCookie } from "../scripts/loginAuthentication.js";
import * as knowledgeAgentFunctions from "../scripts/createPipeline.js";
import { sleep, group } from "k6";
import { textSummary } from 'https://jslib.k6.io/k6-summary/0.0.2/index.js';
let env = process.env.TEST_ENVIRONMENT || "qa"

  export const options = {
    scenarios: {
      per_vu_scenario: {
        executor: "per-vu-iterations", 
        vus: parseInt(process.env.VIRTUAL_USERS) || 10,
        iterations: parseInt(process.env.ITERATIONS) || 1,
        startTime: "0s",
      },
    },
  
    };
export function setup(){
}
  export default function () {
      // For static testing, use hardcoded cookie or get it from login function
      const cookie = process.env.TEST_COOKIE || getAuthCookie(env);
      group('Step 1: Get the serving type', function () {
        const result = knowledgeAgentFunctions.getServingTypeUpdated(cookie);
        
        sleep(5);
      });
      
      group('Step 2: Select the serving type', function () {
        const result = knowledgeAgentFunctions.selectServingTypeUpdated(cookie);
       
        sleep(5);
      });
      
      group('Step 3: Add data product overview', function () {
        const result = knowledgeAgentFunctions.addDataProductOverview(cookie);
        
        sleep(5);
      });
      
      group('Step 4: Add dataset', function () {
        const result = knowledgeAgentFunctions.addDataset(cookie);
       
        sleep(5);
      });
      
      group('Step 5: Complete data catalogue step', function () {
        const result = knowledgeAgentFunctions.completeDataCatalogueStep(cookie);
        
        sleep(5);
      });
      
      group('Step 6: Complete data serving step', function () {
        const result = knowledgeAgentFunctions.completeDataServingStep(cookie);
       
        sleep(5);
      });
      
      group('Step 7: Add governance', function () {
        const result = knowledgeAgentFunctions.addGovernance(cookie);
        
        sleep(5);
      });
      
      group('Step 8: Complete governance step', function () {
        const result = knowledgeAgentFunctions.completeGovernanceStep(cookie);
       
        sleep(5);
      });
      
      group('Step 9: Publish data product', function () {
        const result = knowledgeAgentFunctions.publishDataProduct(cookie);
      
        sleep(5);
      });
  }
export function handleSummary(data) {
    return {
      "../reports/summary.html": htmlReport(data),
      stdout: textSummary(data, { indent: '→', enableColors: true }),
    };
}