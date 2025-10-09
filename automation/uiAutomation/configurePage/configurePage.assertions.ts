import * as locators from "./configurePage.locators"
import * as assertions from "../utils/browserAssertions.utils";
import createExperiment from "../config/modelTraining.json"
import { getTextArray, getTextElement } from "../utils/browserActions.utils";

export async function verifyG2Plot(){
    await locators.g2Plot.waitForDisplayed({timeout: 25000})
}
export async function verifyDefaultFields(expectedTargetColumnText,expectedMethodText){
    let targetColumnText = await getTextElement(locators.getTargetColumn)
    assertions.verifyElementsMatches(targetColumnText,expectedTargetColumnText,"Target Column value not correct")
    console.log(`Default value ${targetColumnText} for Target Column check`)
    let methodText = await getTextElement(locators.getMethod)
    assertions.verifyElementsMatches(methodText,expectedMethodText,"ML Task value not correct")
    console.log(`Default value ${methodText} for ML Task check`)
}
export async function verifyConfigureUIElements(){
    let columnTitlesActual= await getTextArray(locators.columnTitles)
    await assertions.verifyElementIsDisplayed(locators.configureTitle,"The correct configuration title is not displayed",false)
    await assertions.verifyElementIsDisplayed(locators.searchField,"Search field not displayed in configure page",false)
    await assertions.verifyElementsMatches(columnTitlesActual,createExperiment.configureStep.tableheaders,"Incorrect column names are displayed in configure step",false)
    await assertions.verifyElementIsClickable(locators.saveButton,'Save button is not clickable in configure step',false)
    await assertions.verifyElementIsNotClickable(locators.previousBtn,'Previous button is clickable in configure page',false)
}
export async function verifyTSFConfigureUIElements(){
   let actualTimeseriesConfigLabel = await getTextElement(locators.getTSFModalLabel)
   assertions.verifyElementsMatches(actualTimeseriesConfigLabel,createExperiment.configureStep.timeseriesConfigurationLabel,"Time series configuration label not displayed in modal",false)
   await assertions.verifyElementIsClickable(locators.closeButtonTSFConfig,"Close button is not clickable in time series configuraiton modal of configure step",false)
   await assertions.verifyElementIsClickable(locators.closeIconTSFConfig,"Close Icon is not clickable in time series configuraiton modal of configure step",false)
}