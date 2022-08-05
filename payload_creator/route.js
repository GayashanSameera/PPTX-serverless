import {payloadCreatorHandler} from './src/handlers'
import { eventMiddleware } from './src/middlewares'

export const createPayload = async(event) =>  
 eventMiddleware(event,payloadCreatorHandler.createPayload)   
