import {responseHelper} from "../helpers"
import payloadTemplates from "./payloadTemplates"
import {fetchDataResult} from "../helpers/fetchData";
import FORMAL_PROPOSAL1 from "./payloadTemplates/formalProposal1";
import { hooks } from "./hooks";
import { generateKey } from "crypto";


const payloadCreatorHandler={
  

   createPayload:async (event)=>{
    let updatedTempalate={};
     
    
    try{
      const {schemeId,scheme,templateKey,outPutFileName,destBucketName,destPath} = event.body;
       //read selected template
       
       console.log("event",templateKey)
      const payloadTemplate=await payloadTemplates[templateKey](event)
      

     
      // fetch data using template keys
      console.log("Template",FORMAL_PROPOSAL1);
      const fetchDataResult= await fetchDataResult.fetchData(event,FORMAL_PROPOSAL1)

      //hooks for update template using fetced data
      if(generateTemplate[templateKey]){
        
       return updatedTempalate= await generateTemplate[templateKey](payloadTemplate,fetchDataResult)
       
      }
      // return responseHelper.successResponse(event,'Successfully Fetched Template',updatedTemplate,true)
      

    }catch(error){
      console.log("dsdfsdfsd",error);
      
      return responseHelper.errorResponse(event,500,"create payload Failed")

    }
   },


   generatePPTX: async (event) => {
    
  
    
    //createPayload
    //get responce from createPayload
    try {
      const template =await payloadCreatorHandler.createPayload(event);
      console.log('sdasdasdasdasdasdsa',template);
      return responseHelper.successResponse(event,'Successfully Fetched Template',template,true)

    } catch (error) {
      console.log("PaAYLOAD CREATOR ERROR",error)
      return responseHelper.errorResponse(event,500,"create payload Failed")
    }

  
    
    //call to python service using  createPayload responce 


  }


}


export default payloadCreatorHandler;