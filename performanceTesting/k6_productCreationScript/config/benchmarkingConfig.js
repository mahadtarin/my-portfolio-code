module.exports = {
    "knowledgeAgent":{
        description: process.env.KNOWLEDGE_AGENT_DESCRIPTION || "Performance testing knowledge agent for benchmarking data products"
    },
    "performance": {
        virtualUsers: parseInt(process.env.VIRTUAL_USERS) || 10,
        iterations: parseInt(process.env.ITERATIONS) || 1,
        duration: process.env.DURATION || "30s"
    },
    "dataProduct": {
        dataDomain: process.env.DATA_DOMAIN || "sales",
        knowledgeBaseId: process.env.KNOWLEDGE_BASE_ID || "your-knowledge-base-id",
        workspaceId: parseInt(process.env.WORKSPACE_ID) || 67,
        ownerId: parseInt(process.env.OWNER_ID) || 191,
        domainId: parseInt(process.env.DOMAIN_ID) || 52
    }
}