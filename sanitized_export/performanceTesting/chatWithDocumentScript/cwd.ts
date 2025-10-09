const axios = require('axios');
import * as fs from 'fs';
const { promisify } = require('util'); 
const writeFile = promisify(fs.writeFile);
const appendFile = promisify(fs.appendFile);
const questions = process.env.TEST_QUESTIONS 
    ? JSON.parse(process.env.TEST_QUESTIONS)
    : [
        "What information can you provide about this dataset?",
        "How can I analyze the data in this knowledge base?",
        "What are the key insights available?",
        "Can you summarize the main topics covered?",
        "What patterns or trends are visible in the data?"
        // Add more questions as needed
    ];
let currentQuestionIndex = 0;
const getRandomQuestion = () => {
    const question = questions[currentQuestionIndex];
    currentQuestionIndex = (currentQuestionIndex + 1) % questions.length;
    console.log("index", currentQuestionIndex);
    return question;
};
function createPayload() {
    const userMessage = getRandomQuestion();
    return JSON.stringify(
        {
            "temperature": parseFloat(process.env.TEMPERATURE || "0.5"),
            "responseLength": parseInt(process.env.RESPONSE_LENGTH || "2048"),
            "penalty": parseFloat(process.env.PENALTY || "1"),
            "enableApi": process.env.ENABLE_API === 'true' || true,
            "enablePublicAccess": process.env.ENABLE_PUBLIC_ACCESS === 'true' || false,
            "similaritySearchThreshold": parseFloat(process.env.SIMILARITY_THRESHOLD || "0.6"),
            "languageModel": process.env.LANGUAGE_MODEL_ID || "your-language-model-id",
            "llmModelId": process.env.LLM_MODEL_ID || "your-llm-model-id",
            "content": userMessage,
            "origin": process.env.ORIGIN || "data_product",
            "language": process.env.LANGUAGE || "english",
            "dataProductId": process.env.DATA_PRODUCT_ID || "your-data-product-id",
            "knowledgeBaseIds": process.env.KNOWLEDGE_BASE_IDS ? JSON.parse(process.env.KNOWLEDGE_BASE_IDS) : ["your-knowledge-base-id"],
            "openAiIntegrationId": process.env.OPENAI_INTEGRATION_ID || "your-openai-integration-id"
        }
    );
}

const logFilePath = process.env.LOG_FILE_PATH || 'request_logs.csv';

// Initialize CSV file with headers
const initCsvFile = async () => {
    const headers = 'Request ID,Time Sent,Time to First Chunk (seconds),Total Time (seconds),Status,Response\n';
    await writeFile(logFilePath, headers);
};

// Function to log data to CSV
const logToCsv = async (logData) => {
    const csvRow = `${logData.requestId},${logData.timeSent},${logData.timeToFirstChunk},${logData.totalTime},${logData.status},${logData.responseStatus},${logData.response}\n`;
    await appendFile(logFilePath, csvRow);
};

// Function to perform the request and log data
const fetchData = async (requestId) => {
    const startTime = new Date().getTime();
    const timeSent = new Date(startTime).toString();

    try {
        const apiBaseUrl = process.env.API_BASE_URL || 'https://app.your-domain.com';
        const config = {
            method: 'get',
            maxBodyLength: Infinity,
            url: `${apiBaseUrl}/chat-service/api/v1/conversation/documents/stream/chat/?body=${createPayload()}`,
            headers: { 
                'accept': 'text/event-stream', 
                'accept-language': 'en-US,en;q=0.9', 
                'cache-control': 'no-cache', 
                'cookie': process.env.AUTH_COOKIE || 'your_authentication_cookie_here', 
            },
                // data: createPayload(),
            responseType: 'stream'
        };
        const response = await axios.request(config);

        let data = '';
        let firstChunkTime:any = null;
        response.data.on('data', (chunk) => {

         if (firstChunkTime === null) {
                console.log(chunk.toString('UTF-8'))
                firstChunkTime = new Date().getTime();
                const timeToFirstChunk = (firstChunkTime - startTime) / 1000;
                // Log the time to first chunk immediately
                console.log(`Request ${requestId} - First chunk received at: ${firstChunkTime}`);
                console.log(`Request ${requestId} - Time to first chunk (seconds): ${timeToFirstChunk}`);

        }
            data += chunk.toString('utf-8');
        });

        response.data.on('data', (chunk) => {
            if (firstChunkTime === null) {
                firstChunkTime = new Date().getTime();
                const timeToFirstChunk = (firstChunkTime - startTime) / 1000;
                console.log(`Request ${requestId} - First chunk received at: ${firstChunkTime}`);
                console.log(`Request ${requestId} - Time to first chunk (seconds): ${timeToFirstChunk}`);
            }
            data += chunk.toString('utf-8');
        });

        response.data.on('end', async () => {
            const endTime = new Date().getTime();
            const totalTime = (endTime - startTime) / 1000;
            const logData = {
                requestId,
                timeSent,
                timeToFirstChunk: firstChunkTime ? (firstChunkTime - startTime) / 1000 : 'N/A',
                totalTime,
                status: response.status,
                responseStatus: "completed",
                response: data.replace(/\n/g, ' ')
            };

            console.log(`Request ${requestId} - Response completed at: ${endTime}`);
            console.log(`Request ${requestId} - Total time to complete response (seconds): ${totalTime}`);
            await logToCsv(logData);
        });

        response.data.on('error', async (err) => {
            const endTime = new Date().getTime();
            const totalTime = (endTime - startTime) / 1000;
            const logData = {
                requestId,
                timeSent,
                timeToFirstChunk: firstChunkTime ? (firstChunkTime - startTime) / 1000 : 'N/A',
                totalTime,
                status: response.status,
                responseStatus: err.message,
                response: data.replace(/\n/g, ' ')
            };

            console.error(`Request ${requestId} - Error: ${err.message}`);
            console.log(`Request ${requestId} - Response completed at: ${endTime}`);
            console.log(`Request ${requestId} - Total time to complete error (seconds): ${totalTime}`);
            await logToCsv(logData);
        });

    } catch (error:any) {
        const endTime = new Date().getTime();
        const logData = {
            requestId,
            timeSent,
            timeToFirstChunk: 'N/A',
            totalTime: (endTime - startTime) / 1000,
            status: `Failed - ${error.message}`,
            response: 'N/A'
        };
        await logToCsv(logData);
    }
};

// Function to execute concurrent requests
const executeConcurrentRequests = async (numRequests, durationMinutes) => {
    await initCsvFile();
    const intervalMilliseconds = (durationMinutes * 60 * 1000) / numRequests;

    let requestCounter = 0;

    const intervalId = setInterval(() => {
        if (requestCounter >= numRequests) {
            clearInterval(intervalId);
            return;
        }
        requestCounter++;
        const delay = intervalMilliseconds; // Randomize within the interval
        setTimeout(() => {
            console.log(`Request ${requestCounter} - Sending request at: ${new Date().toString()}`);
            fetchData(requestCounter);
        }, delay);

    }, intervalMilliseconds);

};

// Configurable performance test execution
const numRequests = parseInt(process.env.NUM_REQUESTS || "10");
const durationMinutes = parseFloat(process.env.DURATION_MINUTES || "1");
console.log(`Starting performance test: ${numRequests} requests over ${durationMinutes} minute(s)`);
executeConcurrentRequests(numRequests, durationMinutes);