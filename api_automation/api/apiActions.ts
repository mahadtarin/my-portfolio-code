import axios from 'axios';

export const login = async (baseURL: string, requestBody: any) => {
    const response = await axios.post(`${baseURL}/auth/login/`, requestBody, {
        headers: {
            "Content-Type": "application/json",
        },
    });
    return response;
};

export const getListingData = async (baseURL: string, authToken: string) => {
    const response = await axios.get(`${baseURL}/documents/?page=1`, {
        headers: {
            "Authorization": `Bearer ${authToken}`
        }
    });
    return response;
};

export const getDocumentDetails = async (baseURL: string, documentID: string, authToken: string) => {
    const response = await axios.get(`${baseURL}/documents/${documentID}/`, {
        headers: {
            "Authorization": `Bearer ${authToken}`
        }
    });
    return response;
};
export const getContentAPI = async (baseURL: string) => {
    const response = await axios.get(`${baseURL}`, {
    });
    return response;
};
export const publishDocument = async (baseURL: string, documentID: string, requestBody: any, authToken: string) => {
    const response = await axios.put(`${baseURL}/documents/${documentID}/`, requestBody, {
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${authToken}`
        },
    });
    return response;
};

export const editDocument = async (baseURL: string, documentID: string, requestBody: any, authToken: string) => {
    const response = await axios.put(`${baseURL}/documents/${documentID}/`, requestBody, {
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${authToken}`
        },
    });
    return response;
};