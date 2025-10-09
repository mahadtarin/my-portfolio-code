import { Given, Then, When } from '@wdio/cucumber-framework';
// Import statements - Update these paths according to your project structure
import * as s3GetKeys from '@wdio-dBVerification/amazonS3/dbAssertionsS3';
import * as sqlTransformationActions from '@wdio-ui/dataTransformation/sqlTransformationPage/sqlTransformationMainPage/sqlTransformation.tasks';
import * as loginActions from '@wdio-ui/authFlows/login/login.tasks';
import * as configureTasks from '@wdio-ui/modelTraining/configurePage/configurePage.tasks';
import * as configureAssertions from '@wdio-ui/modelTraining/configurePage/configurePage.assertions';
import * as trainingModel from '@wdio-ui/modelTraining/TrainPage/trainPage.tasks';
import * as testModel from '@wdio-ui/modelTraining/testPage/testPage.tasks';
import * as testModelAssertions from '@wdio-ui/modelTraining/testPage/testPage.assertions';
import * as config from './modelTrainingConfig.json';
import * as trainedModel from '@wdio-ui/modelTraining/trainedModels/trainedModels.tasks';
import * as trainedModelAssertions from '@wdio-ui/modelTraining/trainedModels/trainedModels.assertions';
import * as dataCatalogueTasks from '@wdio-ui/commonPages/dataCataloguePage/dataCatalogueMainPage/dataCatalogue.tasks';
import * as s3Functions from '@wdio-dBVerification/amazonS3/modelTrainingVerification/modelTrainingVerification';
import * as pipelineConfig from '@wdio-config/piplineInfoConfig/pipelineConfig.json';
import * as sqlTransformationAPIFuntions from '@wdio-dpsWorkflows/dpsFeaturesFlowsApis/sqlTransformationsThroughApi';
import * as pipelineAPIFunctions from '@wdio-dpsWorkflows/dpsFeaturesFlowsApis/pipelinesThroughApi';
import sourceConfiguration from '@wdio-config/sourcesConfigForApiFunctions/ConnectorsConfigForApiCall.json';
import * as commonActions from '@wdio-ui/dataPipelines/commonFunctions/commonActions';
import * as previewDataCatalogueActions from '@wdio-ui/commonPages/dataCataloguePage/previewCataloguePage/previewCatalogueAction.tasks';
import * as trainPageAssertions from '@wdio-ui/modelTraining/TrainPage/trainPage.assertions';
import * as trainedModelsListing from '@wdio-ui/modelTraining/trainedModelsListing/trainedModelsListing.assertions';
import * as trainedModelsListingActions from '@wdio-ui/modelTraining/trainedModelsListing/trainedModelsListing.tasks';
import modelTraining from '@wdio-config/uiVerifications/modelTraining.json';
import s3Configurations from '@wdio-config/connectorConfigs/connectors.autoQA.json';
import assert from 'soft-assert';
let name ;
let idSql: any ;
let schemaName,s3FlowKeys ;
let type = 'Time series forecasting';
let productName = 'productTSF' + Math.random().toString(10).substring(2, 5);
let sqlTableName ;
let datasetName ;
let versionName ;
Given(
  'User logins in to dps app to train model for time series forecasting',
  async () => {
    await loginActions.openLoginPage();
    await loginActions.login();
    await browser.url('https://your-app-url.com/sign-in')
  }
);
When(
  'User gets the cookies to create google sheets pipeline through api for time series forecasting',
  { timeout: 90000000 },
  async () => {
    // Update these parameters according to your pipeline configuration
    name = await pipelineAPIFunctions.createPipelineThroughApi(
      '<PIPELINE_PREFIX>',
      '<DESTINATION_NAME>',
      'Google Sheets',
      false,
      config['Time series forecasting'].streamName,
      false,
      sourceConfiguration.connectors['Time series forecasting']
    );
  }
);
When(
  'User creates the sql transformation through Api for time series forecasting',
  { timeout: 90000000 },
  async () => {
    await sqlTransformationActions.openSqlTransformationTab();
    await sqlTransformationActions.clickOnSqlButton();
    schemaName = await sqlTransformationAPIFuntions.schemaRandomNameForSqlApi();
    sqlTableName = sqlTransformationAPIFuntions.randomTableNameGenerator(
      config['Time series forecasting'].tableNameInDB
    );
    let sqlQuery = `CREATE SCHEMA IF NOT EXISTS ${schemaName};
    CREATE TABLE ${schemaName}.${sqlTableName} as (select cast (product_id as integer), cast (sales as integer ),cast (store_id as integer), sale_date from ${name}.${config['Time series forecasting'].tableNameInDB});`;
    idSql =
      await sqlTransformationAPIFuntions.createSqlTransformationThroughApi(
        sqlQuery,
        config['Time series forecasting'].sqlTransformation
      );
  }
);
Given(
  'User navigates to trained models tab for time series forecasting',
  async () => {
    await browser.url(`/trained-models`);
  }
);
When(
  'User selects create experiment with model training option for time series forecasting',
  async () => {
    
    await dataCatalogueTasks.clickCreateExperiment();
    await dataCatalogueTasks.searchFieldCheckModelTraining(sqlTableName);
    await dataCatalogueTasks.clickDatasetRadioBtn(sqlTableName);
    await dataCatalogueTasks.clickAddDatasetBtn();
  }
);
Given('User selects target column for time series forecasting', async () => {
  await configureTasks.selectTargetColumn(
    config['Time series forecasting'].targetColumn
  );
});
Then(
  'User verifies profiling for target column with time series forecasting',
  async () => {
    // await configureAssertions.verifyG2Plot()
  }
);
When('User selects ML task for time series forecasting', async () => {
  await configureTasks.selectMLTask(type);
});
Then(
  'User fills out ML task configuration form for time series forecasting',
  async () => {
    await configureTasks.clickConfigTSF();
    await configureTasks.configureTSF(
      config['Time series forecasting'].itemIDColumn,
      config['Time series forecasting'].timestampColumn,
      config['Time series forecasting'].groupColumn
    );
  }
);

Then(
  'User verifies UI elements of time series forecasting form', 
  async () => {
  await configureAssertions.verifyTSFConfigureUIElements();
  await configureTasks.applyConfigure();
});

When(
  'User selects all columns for time series forecasting',
   async () => {
  await configureTasks.selectAllColumns();
});

Then(
  'User verifies UI elements of configuration step for time series forecasting',
  async () => {
    await configureAssertions.verifyConfigureUIElements();
    await configureTasks.clickNextBtn();
  }
);
When(
  'User selects the memory for model training and trains model for time series forecasting',
  { timeout: 90000000 },
  async () => {
    await trainingModel.computeInstance();
  }
);
When('User aborts the model training for time series forecasting', async () => {
  await trainingModel.abortTraining();
});
Then(
  'User retrains the model for time series forecasting',
 async () => {
  await trainingModel.startModelTraining();
  await trainPageAssertions.verifyModelTrainingCompleted();
  await configureTasks.clickNextBtn();
  await browser.pause(5000)
  
});
Given(
  'User lands on the validation page for time series forecasting',
  async () => {
    await browser.pause(5000)
    await testModelAssertions.verifyUIElementsTestModel(type);
  }
);
Then(
  'User gets the keys from the s3 bucket for time series forecasting',
  async () => {
    let s3Keys = await s3GetKeys.getKeys(
      `${s3Configurations.destination.s3.bucketName}/${sqlTableName}`
    );
    datasetName = await commonActions.getNameofPipelineS3(sqlTableName, s3Keys);
    await s3GetKeys.getKeys(
      `${s3Configurations.destination.s3.bucketName}/${datasetName}`
    );
    await s3Functions.getS3StatsForModelTraining(
      datasetName,
      config['Time series forecasting'].filePath,
      config.validationArtifactsFilePath,
      config.performanceMetricsFilePath,
      config.fileExtension
    );
    await browser.pause(5000);
  }
);
Then(
  'Verify model stats on the validation step for time series forecasting',
  async () => {
    await browser.refresh();
    await testModelAssertions.verifyF1ScoreForMultiClassification(
      s3Functions.exportStats[0]
    );
    await testModel.viewAdvancedMetricsModal();
    await testModel.clickPerformanceTab();
    versionName = await testModel.getModelVersion();
    await testModelAssertions.verifyPerformanceTSF();
    await testModel.clickExpandibilityTab();
    await testModelAssertions.verifyMetricsTSF(
      s3Functions.exportStats[0],
      s3Functions.exportStats[1],
      s3Functions.exportStats[2]
    );
    await testModelAssertions.verifyColumns(
      config['Time series forecasting'].targetColumn,
      config['Time series forecasting'].itemIDColumn,
      config['Time series forecasting'].groupColumn,
      config['Time series forecasting'].timestampColumn
    );
  }
);
Then(
  'Verify model is publised for time series forecasting',
   async () => {
  await testModel.closeAdvanceMetricsModal();
  await testModel.publishModel();
});
Then(
  'Verify model stats from the published model view details for time series forecasting',
  async () => {
    await browser.refresh();
    await previewDataCatalogueActions.scrollToWidget('Trained Models');
    await trainedModel.expandExperiment();
    await trainedModelAssertions.verifyExperimentInListing(
      modelTraining.trainedModelsListing.status,
      s3Functions.exportStats[0],
      versionName,
      type
    );
    await trainedModel.clickViewDetailsIcon();
    await testModel.clickPerformanceTab();
    await testModelAssertions.verifyPerformanceTSF();
    await testModel.clickExpandibilityTab();
    await testModelAssertions.verifyMetricsTSF(
      s3Functions.exportStats[0],
      s3Functions.exportStats[1],
      s3Functions.exportStats[2]
    );
    await testModelAssertions.verifyColumns(
      config['Time series forecasting'].targetColumn,
      config['Time series forecasting'].itemIDColumn,
      config['Time series forecasting'].groupColumn,
      config['Time series forecasting'].timestampColumn
    );
    await testModel.closeAdvanceMetricsModal();
    assert.softAssertAll();
  }
);
Given(
  'User clicks mark for product icon for time series forecasting model',
  async () => {
    await trainedModel.markforProduct()
  }
);
When(
  'User fills mark for product form for time series forecasting model',
  async () => {
    await trainedModel.configureProduct(productName)
    versionName = productName
  }
);
Then(
  'User verifies that time series forecasting model is deployed',
  async () => {
    // await trainedModelAssertions.verifyModelDeployment()
  }
);
Given(
  'User deletes the sql transformation and pipeline for system cleanup for time series forecasting',
  async () => {
    await testModel.closeAdvanceMetricsModal();
    // await pipelineAPIFunctions.disablePipelineThroughApi()
    // await sqlTransformationAPIFuntions.disableSqlTransformationFromUiThroughApi(idSql)
    // await dbAssertions.deleteSchema(schemaName);
    // await dbAssertions.deleteSchema(name);
    assert.softAssertAll()
  }
);
Then(
  'Verify model training stats in listing for time series forcasting',
  async () => {
    await trainedModelsListing.verifyTrainedModelInListing(
      versionName,
      s3Functions.exportStats[0],
      sqlTableName,
      type,
      config['Time series forecasting'].targetColumn,
      modelTraining.trainedModelsListing.status,
      type
    );
  }
);
Then(
  'Verify view details for time series forecasting in listing',
   async () => {
  s3FlowKeys = s3GetKeys.keys
  await trainedModelsListingActions.hoverOverModelTrainingActionsButton(
    versionName
  );
  await testModel.clickPerformanceTab();
  await testModelAssertions.verifyPerformanceTSF();
  await testModel.clickExpandibilityTab();
  await testModelAssertions.verifyMetricsTSF(
    s3Functions.exportStats[0],
    s3Functions.exportStats[1],
    s3Functions.exportStats[2]
  );
  await testModelAssertions.verifyColumns(
    config['Time series forecasting'].targetColumn,
    config['Time series forecasting'].itemIDColumn,
    config['Time series forecasting'].groupColumn,
    config['Time series forecasting'].timestampColumn
  );
  assert.softAssertAll();
});
Given(
  'User is at data Catalogue Page and selects the data Asset and jumps to preview page for Time series forecasting',
  async () => {
    await browser.url("/assets")
    await dataCatalogueTasks.searchFieldCheckModelTraining(sqlTableName);
    await dataCatalogueTasks.clickDataset(sqlTableName)
  } 
);
When(
  'User scrolls down to Trained Model widget and verifies that experiment exists in the table for Time series forecasting',
  async () => {
    await previewDataCatalogueActions.scrollToWidget("Trained Models")
  }
)
Then(
  'User clicks on the Add Version button for the respective experiment for Time series forecasting',
  async () => {
    await previewDataCatalogueActions.clickOnAddVersionButton()
    const windowHandles = await browser.getWindowHandles();
    console.log(windowHandles);
    await browser.pause(2000);
    await browser.switchToWindow(windowHandles[1]);
    const url= await browser.getUrl();
    await browser.pause(5000)
    await browser.closeWindow();
    await browser.pause(5000)
    await browser.switchToWindow(windowHandles[0]);
    await browser.pause(5000)
    await browser.url(url)
  }
)
Then(
  'User verifies the default fields on the configure page for time series forecasting',
  async () => {
    await configureAssertions.verifyDefaultFields(config['Time series forecasting'].targetColumn,type)
  }
)
Then(
  'User gets the keys from the s3 bucket for time series forecasting add version flow',
  async () => {
    let s3Keys = await s3GetKeys.getKeys(
      `${s3Configurations.destination.s3.bucketName}/${sqlTableName}`
    );
    datasetName = await commonActions.getNameofPipelineS3(sqlTableName, s3Keys);
    await s3GetKeys.getKeys(
      `${s3Configurations.destination.s3.bucketName}/${datasetName}`
    );
    await s3GetKeys.getUniqueKeys(s3FlowKeys);
    await s3Functions.getS3StatsForModelTraining(
      datasetName,
      config['Time series forecasting'].filePath,
      config.validationArtifactsFilePath,
      config.performanceMetricsFilePath,
      config.fileExtension
    );
    await browser.pause(5000);
  }
);
Then(
  'User verifies the model training is completed for time series forecasting',
   async () => {
  await trainPageAssertions.verifyModelTrainingCompleted();
  await configureTasks.clickNextBtn();
  await browser.pause(5000)
});