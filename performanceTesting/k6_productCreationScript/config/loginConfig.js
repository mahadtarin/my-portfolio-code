module.exports= {
    "loginConfig":{ 
        "dev" :{
        "workspace": process.env.WORKSPACE_NAME || "your_workspace",
        "username": process.env.DEV_USERNAME || "your_username@domain.com",
        "password": process.env.DEV_PASSWORD || "your_password"
    },
        "qa" :{
        "workspace": process.env.WORKSPACE_NAME || "your_workspace",
        "username": process.env.QA_USERNAME || "your_username@domain.com",
        "password": process.env.QA_PASSWORD || "your_password"
    },
        "staging" :{
        "workspace": process.env.WORKSPACE_NAME || "your_workspace",
        "username": process.env.STAGING_USERNAME || "your_username@domain.com",
        "password": process.env.STAGING_PASSWORD || "your_password"
    },
},
}