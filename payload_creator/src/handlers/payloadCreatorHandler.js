import responseHelper from "../helpers"
import payloadTemplates from "./payloadTemplates"


const payloadCreatorHandler={
   createPayload:(event)=>{
     
    
    try{
      const {schemeId,scheme,templateKey,outPutFileName,destBucketName,destPath} = event.body;
      const payloadTemplate=await payloadTemplates[templateKey](event)

      return responseHelper.successResponse(event,'Successfully Fetched Template',payloadTemplate,true)
      

    }catch{
      return responseHelper.errorResponse(event,500,"create payload Failed")

    }
   } 
}
export default payloadCreatorHandler;