import * as browserActions from "../utils/browserActions.utils"
import * as locators from "./configurePage.locators"
import * as assertions from "./configurePage.assertions"
export async function selectTargetColumn(column){
 await browserActions.dropDownSelect(locators.targetColumn,locators.selectDropdownOption(column))
}
export async function selectMLTask(mlTask){
    await browserActions.dropDownSelect(locators.mlTask,locators.selectDropdownOption(mlTask))
}
export async function selectAllColumns(){
   await browserActions.dropDownSelect(locators.getColumnsTablePaginationCount,locators.selectDropdownValue('25'))
   await $(locators.headerCheckBox).scrollIntoView({block :'center'})
   await browserActions.waitAndClick(locators.headerCheckBox)
}
export async function clickConfigTSF(){
    await browserActions.waitAndClick(locators.configTSF)
}
export async function configureTSF(itemIDColumn,timeStampColumn,groupColumn){
   await browserActions.dropDownSelect(locators.itemIDColumn,locators.selectDropdownOption(itemIDColumn))
//    await browserActions.dropDownSelect(locators.groupColumn,locators.selectDropdownOption(groupColumn))
//    await browserActions.dropDownSelect(locators.groups,locators.selectDropdownOption('154'))
//    await locators.groups.click()
//    await browserActions.dropDownSelect(locators.groups,locators.selectDropdownOption('199'))
//    await locators.groups.click()
    // console.log("Add ")
    // await browser.pause(25000)
   await browserActions.dropDownSelect(locators.timeStampColumn,locators.selectDropdownOption(timeStampColumn))
}

export async function applyConfigure(){
    await $(locators.applyButton).scrollIntoView({block: 'center'});
    await browserActions.waitAndClick(locators.applyButton)
}
export async function clickNextBtn(){
    await $(locators.nextBtn).scrollIntoView({block: 'center'});
    await $(locators.nextBtn).waitForClickable({timeout:30000})
    await browserActions.waitAndClick(locators.nextBtn)
}
export async function configureMultiClassification (column,mlTask){
    await selectTargetColumn(column);
    await assertions.verifyG2Plot();
    await selectMLTask(mlTask)
    // await browserActions.waitAndClick(locators.getSelectAlgorithmButton);
    // await browserActions.dropDownSelect(locators.getPaginationBar,locators.selectDropdownValue('25'))
    // await $(locators.getSelectAlgorithmHeaderCheckBox).scrollIntoView({block : 'center'})
    // await browserActions.waitAndClick(locators.getSelectAlgorithmHeaderCheckBox)
    // await browserActions.waitAndClick(locators.getRandomForestClassifier);
    // await browserActions.waitAndClick(locators.getApplyButton);
    await selectAllColumns();
    await clickNextBtn();
}