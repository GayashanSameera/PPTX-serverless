import responseHelper from "../helpers"
import payloadTemplates from "./payloadTemplates"
import fetchDataResult from "../helpers/fetchData";
import formalProposal1 from "./payloadTemplates/formalProposal1";
import { hooks } from "./hooks";
import { generateKey } from "crypto";


const payloadCreatorHandler={
  generatePPTX: async (event) => {
    
    console.log("Testinmg ",JSON.stringify(event));
    
    //createPayload
    //get responce from createPayload
    try {
      const template = createPayload(event);
      return responseHelper.successResponse(event,'Successfully Fetched Template',template,true)

    } catch (error) {
      return responseHelper.errorResponse(event,500,"create payload Failed")
    }

  
    
    //call to python service using  createPayload responce 


  },

   createPayload:async (event)=>{
    let updatedTempalate={};
     
    
    try{
      const {schemeId,scheme,templateKey,outPutFileName,destBucketName,destPath} = event.body;
       //read selected template
      const payloadTemplate=await payloadTemplates[templateKey](event)

     
      // fetch data using template keys
      const fetchDataResult= await fetchDataResult.fetchData(event,formalProposal1)

      //hooks for update template using fetced data
      if(generateTemplate[templateKey]){
        
       return updatedTempalate= await generateTemplate[templateKey](payloadTemplate,fetchDataResult)
       
      }
      // return responseHelper.successResponse(event,'Successfully Fetched Template',updatedTemplate,true)
      

    }catch{
      return responseHelper.errorResponse(event,500,"create payload Failed")

    }
   } 
}
export default payloadCreatorHandler;