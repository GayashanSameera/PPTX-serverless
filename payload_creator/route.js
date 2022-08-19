import {payloadCreatorHandler} from './src/handlers'
import  eventMiddleware  from './src/middlewares'
// import requestPPTXValidator from './src/middlewares/payloadCreatorMiddleware'
import payloadCreatorMiddleware from './src/middlewares/payloadCreatorMiddleware.js'

// export const createPayload = async(event) =>  
//  eventMiddleware(event,payloadCreatorHandler.createPayload)   

export const generatePPTX = async(event)  => 
await eventMiddleware
(
    event,
    payloadCreatorMiddleware.requestPPTXValidator,
    payloadCreatorHandler.generatePPTX
)   
 
