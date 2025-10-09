import http from "k6/http";
import { sleep } from "k6";
export function logout(cookie){
    const params = {
        headers: {
          'cache-control': 'max-age=0',
          'Content-Type': 'application/json', 
          'cookie': `${cookie}`
        }
    }
    sleep(3)
    const logoutUrl = process.env.LOGOUT_BASE_URL || `https://${__ENV.envName}.your-domain.com`;
    let userLogout = http.post(`${logoutUrl}/auth-service-keycloak/api/v1/users/logout/`,null,params)
    console.log(userLogout.json())
}