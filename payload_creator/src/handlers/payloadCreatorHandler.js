import {responseHelper,fetchDataResult} from "../helpers"
import * as payloadTemplates from "./payloadTemplates"
//import {fetchDataResult} from "../helpers/fetchData";
//import FORMAL_PROPOSAL1 from "./payloadTemplates/formalProposal1";
import { generatedTemplate } from "./hooks";
import { generateKey } from "crypto";


const payloadCreatorHandler={
  

   createPayload:async (event)=>{
    let updatedTemplate={};
     
    
    try{
      const {schemeId,scheme,templateKey,outPutFileName,destBucketName,destPath} = event.body;
       //read selected template
       
       console.log("event",templateKey)
      const payloadTemplate= payloadTemplates[templateKey]
      
      console.log("payloadTemplate",payloadTemplate);
     
      // fetch data using template keys
      const fetchedData= await fetchDataResult.fetchData(event,payloadTemplate);
      console.log("fetchedData",fetchedData);

      //hooks for update template using fetched data
      if(generatedTemplate[templateKey]){
        
       return updatedTemplate= await generatedTemplate[templateKey](payloadTemplate,fetchedData)
       
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