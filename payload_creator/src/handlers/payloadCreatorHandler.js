import responseHelper from "../helpers"
import payloadTemplates from "./payloadTemplates"


const payloadCreatorHandler={
  generatePPTX: () => {
    //createPayload
    //get responce from createPayload
    //call to python service using  createPayload responce 
  },

   createPayload:(event)=>{
     
    
    try{
      const {schemeId,scheme,templateKey,outPutFileName,destBucketName,destPath} = event.body;
      const payloadTemplate=await payloadTemplates[templateKey](event)

      //read selected template

      // fetch data using template keys

      //hooks for update template using fetced data

      return responseHelper.successResponse(event,'Successfully Fetched Template',payloadTemplate,true)
      

    }catch{
      return responseHelper.errorResponse(event,500,"create payload Failed")

    }
   } 
}
export default payloadCreatorHandler;