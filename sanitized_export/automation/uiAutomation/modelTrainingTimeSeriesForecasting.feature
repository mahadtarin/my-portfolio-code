@timeSeriesForecasting @modelTraining @timeagain @release
Feature: User performs model training with time series forecasting 

    Scenario: User performs the pre reqs steps for model training flow
        Given User logins in to dps app to train model for time series forecasting
        When User gets the cookies to create google sheets pipeline through api for time series forecasting
        When User creates the sql transformation through Api for time series forecasting

    Scenario: User starts the model training flow through Data Catalogue tab
        Given User navigates to trained models tab for time series forecasting
        When User selects create experiment with model training option for time series forecasting 
    
    Scenario: User fills configuration details for model training flow
        Given User selects target column for time series forecasting
        Then User verifies profiling for target column with time series forecasting
        When User selects ML task for time series forecasting
        When User fills out ML task configuration form for time series forecasting
        Then User verifies UI elements of time series forecasting form
        When User selects all columns for time series forecasting
        Then User verifies UI elements of configuration step for time series forecasting

    Scenario: User trains model and verifies the result
        When User selects the memory for model training and trains model for time series forecasting
        When User aborts the model training for time series forecasting
        When User retrains the model for time series forecasting

    Scenario: User moves to next step of validation
        Given User lands on the validation page for time series forecasting
        When User gets the keys from the s3 bucket for time series forecasting
        Then Verify model stats on the validation step for time series forecasting

    Scenario: User publishes the model for time series forecasting
        Then Verify model is publised for time series forecasting
        Then Verify model stats from the published model view details for time series forecasting

    Scenario: User marks time series forecasting model for product
        Given User clicks mark for product icon for time series forecasting model
        When User fills mark for product form for time series forecasting model
        Then User verifies that time series forecasting model is deployed

    Scenario: User navigates to trained models listing tab after creating time series forcasting model
        Given User navigates to trained models tab for time series forecasting
        Then Verify model training stats in listing for time series forcasting
        Then Verify view details for time series forecasting in listing

    Scenario: User navigates to data Catalogue Page and performs actions on data Asset
        Given User is at data Catalogue Page and selects the data Asset and jumps to preview page for Time series forecasting
        When User scrolls down to Trained Model widget and verifies that experiment exists in the table for Time series forecasting
        Then User clicks on the Add Version button for the respective experiment for Time series forecasting 

     Scenario: User fills configuration details for model training flow
        When User fills out ML task configuration form for time series forecasting
        Then User verifies UI elements of time series forecasting form
        When User selects all columns for time series forecasting
        Then User verifies the default fields on the configure page for time series forecasting
        Then User verifies UI elements of configuration step for time series forecasting

    Scenario: User trains model and verifies the result
        When User selects the memory for model training and trains model for time series forecasting
        Then User verifies the model training is completed for time series forecasting

    Scenario: User moves to next step of validation
        Given User lands on the validation page for time series forecasting
        When User gets the keys from the s3 bucket for time series forecasting add version flow
        Then Verify model stats on the validation step for time series forecasting

    Scenario: User publishes the model for time series forecasting
        Then Verify model is publised for time series forecasting
        Then Verify model stats from the published model view details for time series forecasting

    Scenario: User navigates to trained models listing tab after creating time series forcasting model
        Given User navigates to trained models tab for time series forecasting
        Then Verify model training stats in listing for time series forcasting
        Then Verify view details for time series forecasting in listing
    
    Scenario: User deletes the model, sql transformation and pipeline
        Given User deletes the sql transformation and pipeline for system cleanup for time series forecasting
