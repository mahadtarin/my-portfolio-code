import http from "k6/http";
import { sleep } from "k6";
import { parseHTML } from 'k6/html';
const userConfiguration = require('../config/loginConfig.js')
export function loginToTenantAdmin(envName){
        const baseUrl = process.env.AUTH_BASE_URL || `https://${envName}.your-domain.com`;
        let response = http.getRequest(`${baseUrl}/auth-service-keycloak/api/v1/users/login/?tenantName=${userConfiguration.loginConfig[envName].workspace}`)
        let keycloakUrl = response.data.data.url;
        console.log(keycloakUrl)
        return keycloakUrl
    }
    export function loginToKeycloak(keycloakURL){
        let authSeesionID, authSessionIDLegacy, kcRestart, keycloakUserLoginURL
        let cookiesAndURLObj = {}
        let getCookieAndURL = http.getRequest(keycloakURL)
        authSeesionID = getCookieAndURL.headers['set-cookie'][0].split('AUTH_SESSION_ID=')[1].split(';')[0]
        authSessionIDLegacy = getCookieAndURL.headers['set-cookie'][1].split('AUTH_SESSION_ID_LEGACY=')[1].split(';')[0]
        kcRestart = getCookieAndURL.headers['set-cookie'][2].split('KC_RESTART=')[1].split(';')[0]
        const $ = cheerio.load(response.data);
        const formElement = $('form');
        keycloakUserLoginURL= formElement.attr('action');
        Object.assign(cookiesAndURLObj,{AUTH_SESSION_ID: authSeesionID});
        Object.assign(cookiesAndURLObj,{AUTH_SESSION_ID_LEGACY: authSessionIDLegacy});
        Object.assign(cookiesAndURLObj,{KC_RESTART: kcRestart});
        Object.assign(cookiesAndURLObj,{KEYCLOAK_URL: keycloakUserLoginURL});
        return  cookiesAndURLObj
    }
    export function loginToAPP(keycloak,env){
        let keycloakCallbackURL
        const payload = qs.stringify({
            'username': userConfiguration[env].username,
            'password': userConfiguration[env].password,
            'credentialId': '' 
          });   
        const headers = { 
            'content-type': 'application/x-www-form-urlencoded', 
            'Cookie': `AUTH_SESSION_ID=${keycloak.AUTH_SESSION_ID}; AUTH_SESSION_ID_LEGACY=${keycloak.AUTH_SESSION_ID_LEGACY}; KEYCLOAK_IDENTITY=${keycloak.KC_RESTART}`
        }
        const response = http.post(keycloak.KEYCLOAK_URL, payload, { headers: headers, redirects: 0 });
        keycloakCallbackURL= response.headers.location;
        return keycloakCallbackURL
    }
    export function extractFirstPart(array) {
      return array.map(item => {
        const pathIndex = item.indexOf('; Path=');
        if (pathIndex !== -1) {
          return item.substring(0, pathIndex);
        }
        return item
      });
    }
    export function getCookiesFromCallbackURL(keycloakCallbackURL){
      let cookies
        let authToken
        let response = http.getRequest(keycloakCallbackURL , {maxRedirects: 0})
        cookies = response.headers['set-cookie'];
        cookies = extractFirstPart(cookies)
        authToken = cookies.join(';')
        return authToken
    }
    
    export function getAuthCookie(envName){
        let keycloakURL = loginToTenantAdmin(envName);
        let obj = loginToKeycloak(keycloakURL);
        let keycloakCallbackURL = loginToAPP(obj,envName)
        let authToken = getCookiesFromCallbackURL(keycloakCallbackURL)
        console.log("Login Success")
        return authToken
    }