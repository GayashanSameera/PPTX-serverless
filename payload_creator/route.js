import {payloadCreatorHandler} from './src/handlers'
import { eventMiddleware } from './src/middlewares'
import payloadCreatorMiddleware from './src/middlewares/payloadCreatorMiddleware'

// export const createPayload = async(event) =>  
//  eventMiddleware(event,payloadCreatorHandler.createPayload)   

export const generatePPTX = async(event) =>  
 eventMiddleware(event,payloadCreatorMiddleware.requestPPTXValidator,payloadCreatorHandler.generatePPTX)   
