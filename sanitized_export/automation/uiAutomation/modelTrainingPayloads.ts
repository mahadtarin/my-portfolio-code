
export function MLOverviewPagePayload(targetColumn,supportedModelID,itemIDColumn,timestampColumn){
    return {
        "targetColumn": targetColumn,
        "supportedModelID": supportedModelID,
        "columns": {
          "product_id": {
            "name": "product_id",
            "type": "integer"
          },
          "sale_date": {
            "name": "sale_date",
            "type": "timestamp without time zone"
          },
          "sales": {
            "name": "sales",
            "type": "integer"
          },
          "store_id": {
            "name": "store_id",
            "type": "integer"
          }
        },
        "modelConfig": {
          "item_id_column": {
            "value": itemIDColumn
          },
          "group_column": {
            "value": ""
          },
          "groups": {
            "value": []
          },
          "timestamp_column": {
            "value": timestampColumn
          },
          "validation_test_dataset_percentage": {
            "value": "20"
          }
        },
        "draftingStatus": {
          "1": true,
          "2": false,
          "3": false
        },
        "algorithms": []
      }
}
export function startModelTrainingPayload(trainingInstanceID){
    return{
        "draftingStatus": {
          "1": true,
          "2": false,
          "3": false
        },
        "trainingInstanceID": trainingInstanceID
      }
}
export function startValidationPayload(){
    return {"validationConfig":{}
}
}
export function markForDeploymentPayload(name){
  return {
    "name": name,
    "description": "",
    "tags": []
  }
}