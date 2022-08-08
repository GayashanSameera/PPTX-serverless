import responseHelper from "../helpers"
import payloadTemplates from "./payloadTemplates"
import fetchDataResult from "../helpers/fetchData";
import formalProposal1 from "./payloadTemplates/formalProposal1";
import { hooks } from "./hooks";
import { generateKey } from "crypto";


const payloadCreatorHandler={
  generatePPTX: (event) => {
    
    
    
    //createPayload
    //get responce from createPayload
    const template = createPayload(event);
    
    //call to python service using  createPayload responce 


  },

   createPayload:(event)=>{
     
    
    try{
      const {schemeId,scheme,templateKey,outPutFileName,destBucketName,destPath} = event.body;
       //read selected template
      const payloadTemplate=await payloadTemplates[templateKey](event)

     
      // fetch data using template keys
      const fetchDataResult=fetchDataResult.fetchData(event,formalProposal1)

      //hooks for update template using fetced data
      if(generateTemplate[templateKey]){
      return   generateTemplate[templateKey](payloadTemplate,fetchDataResult)
       generate
      }
      // return responseHelper.successResponse(event,'Successfully Fetched Template',payloadTemplate,true)
      

    }catch{
      return responseHelper.errorResponse(event,500,"create payload Failed")

    }
   } 
}
export default payloadCreatorHandler;