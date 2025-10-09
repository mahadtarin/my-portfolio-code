import * as creds from "../jsonFile/translationReviewPortal.json"
export const requestBody = (subdocID: string[]) => ({
    "subdocs": [
        {
            "id": subdocID[0],
            "englishContent": "QA Testing"
        }
    ],
    "edited": true
});
export const nextPageRequestBody = (subdocID: string[], status_array: string[]) => ({
    "subdocs": [
        {
            "id": `${subdocID}`,
            "status": status_array[1]
        }
    ]
});
export const publishRequestBody = (subdocID: string[], status_array: string[]) => ({
    "subdocs": subdocID.map(id => ({
        "id": id
    })),
    "status": status_array[2], // "PUBLISHED"
});
export const loginPayload = (portal: string, env) => {
    switch (portal) {
        case "translationReview":
            return {
                "email": creds[env].translationReviewCreds.email,
                "password": creds[env].translationReviewCreds.password
            };
        case "englishReview":
            return {
                "email": creds[env].englishReviewCreds.email,
                "password": creds[env].englishReviewCreds.password
            };
        default:
            throw new Error("Invalid portal type");
    }
};
export const editDocumentPayload = (subdocID: string[], metrics) => ({
    "subdocs": [
        {
            "id": subdocID[0],
            "metrics": metrics
        }
    ],
    "edited": true
});