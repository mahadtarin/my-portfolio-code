export const targetColumn= $(`#targetColumn`)
export function selectDropdownOption(option){
    return $(`//div[text()='${option}']`)
}
export const getTargetColumn = $(`//div[@id='targetColumn']/div/div`)
export const getMethod = $(`//div[@id='algorithm']/div/div`)
export const mlTask = $(`#algorithm`)
export const headerCheckBox= (`//span[@data-testid="header-checkbox"]`)
export const itemIDColumn=$(`#idColumn`)
export const groupColumn=$(`#groupColumn`)
export const groups=$(`//div[@class=' css-1d8n9bt']`)
export const timeStampColumn=$(`#timestampColumn`)
export const configTSF=(`#configure-tsf`)
export const applyButton= (`//button[@data-testid="loading-btn"]`)
export const nextBtn=(`#continue-btn-cta-in-progress-bar`)
export const profileFetchingText=$(`//*[text()='Fetching profiling data...']`)
export const helpButton=$(`#help-btn-cta-in-progressb-ar`)
export const columnTitles=(`//thead[@id="table-head"]//div`)
export const searchField=$(`#search`)
export const g2Plot=$(`//div[@data-chart-source-type='G2Plot']`)
export const configureTitle=$(`//p[text()='Configure']`)
export const modelNameTSF=$(`[id="configure-tsf"]`)
export const getTSFModalLabel = $(`//span[@class="modelName"]`)
export const closeButtonTSFConfig=$(`//button[@data-testid='close-btn']`)
export const closeIconTSFConfig=$(`//button[@data-testid='close-icon-btn']`)
export const saveButton=$(`#skip-btn-cta-in-progress-bar`)
export const previousBtn=$(`#previous-btn`)
export const getSelectAlgorithmButton = (`#select-algorithm`);
export const getPaginationBar = $(`//div[@class="pagination-table"]//div[@id="pagination-limit-select-field"]`);
export const getSelectAlgorithmHeaderCheckBox = (`//div[@class="dialog-body"]//span[@data-testid="header-checkbox"]`);
export const getApplyButton = (`//button[@data-testid="loading-btn"]`);
export const getRandomForestClassifier = (`//div[@class="dialog-body"]//tr[10]//td//span[@data-testid="row-undefined-checkbox"]`);
export const getColumnsTablePaginationCount = $(`//div[@aria-labelledby="pagination-limit-select-field"]`);
export function selectDropdownValue(option){
    return $(`//li[@data-value="${option}"]`)
}
